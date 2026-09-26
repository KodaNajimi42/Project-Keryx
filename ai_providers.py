from abc import ABC, abstractmethod

from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types
from openai import AsyncOpenAI, APIStatusError


class AIProviderError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class ImageGenerationUnavailable(AIProviderError):
    pass


class AIProvider(ABC):
    """Vendor-neutral AI interface used by Keryx Discord commands."""

    name = "unknown"
    supports_image_generation = False

    @abstractmethod
    async def generate_text(
        self,
        *,
        model: str,
        prompt: str,
        instructions: str,
        max_output_tokens: int,
    ) -> str:
        raise NotImplementedError

    async def generate_image(self, *, model: str, prompt: str) -> bytes:
        """Reserved for a future `/imagine` command and provider adapters."""
        raise ImageGenerationUnavailable(
            f"Image generation is not implemented for the {self.name} provider."
        )

    async def close(self):
        return None


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    async def generate_text(
        self,
        *,
        model: str,
        prompt: str,
        instructions: str,
        max_output_tokens: int,
    ) -> str:
        try:
            response = await self.client.aio.models.generate_content(
                model=model,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    system_instruction=instructions,
                    max_output_tokens=max_output_tokens,
                    temperature=0.7,
                ),
            )
            return response.text.strip() if response.text else ""
        except genai_errors.APIError as error:
            raise AIProviderError(error.message, error.code) from error

    async def close(self):
        await self.client.aio.aclose()


class ResponsesAPIProvider(AIProvider):
    """OpenAI Responses API adapter, also compatible with xAI's endpoint."""

    def __init__(self, api_key: str, *, name: str, base_url: str | None = None):
        self.name = name
        options = {"api_key": api_key}
        if base_url:
            options["base_url"] = base_url
        self.client = AsyncOpenAI(**options)

    async def generate_text(
        self,
        *,
        model: str,
        prompt: str,
        instructions: str,
        max_output_tokens: int,
    ) -> str:
        try:
            response = await self.client.responses.create(
                model=model,
                instructions=instructions,
                input=prompt,
                max_output_tokens=max_output_tokens,
            )
            return response.output_text.strip()
        except APIStatusError as error:
            raise AIProviderError(str(error), error.status_code) from error

    async def close(self):
        await self.client.close()


def create_ai_provider(
    provider_name: str,
    *,
    gemini_api_key: str = "",
    openai_api_key: str = "",
    xai_api_key: str = "",
    compatible_api_key: str = "",
    compatible_base_url: str = "",
) -> AIProvider | None:
    """Create the configured provider, or return None when its key is absent."""
    provider_name = provider_name.strip().lower()

    if provider_name == "gemini":
        return GeminiProvider(gemini_api_key) if gemini_api_key else None
    if provider_name == "openai":
        return ResponsesAPIProvider(openai_api_key, name="openai") if openai_api_key else None
    if provider_name in {"grok", "xai"}:
        return (
            ResponsesAPIProvider(
                xai_api_key,
                name="grok",
                base_url="https://api.x.ai/v1",
            )
            if xai_api_key
            else None
        )
    if provider_name == "openai-compatible":
        if not compatible_api_key or not compatible_base_url:
            return None
        return ResponsesAPIProvider(
            compatible_api_key,
            name="openai-compatible",
            base_url=compatible_base_url,
        )

    raise ValueError(
        "AI_PROVIDER must be gemini, openai, grok, xai, or openai-compatible."
    )
