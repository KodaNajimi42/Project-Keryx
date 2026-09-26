import unittest

from ai_providers import ImageGenerationUnavailable, create_ai_provider


class AIProviderFactoryTests(unittest.TestCase):
    def test_missing_provider_key_disables_ai(self):
        self.assertIsNone(create_ai_provider("gemini"))
        self.assertIsNone(create_ai_provider("openai"))
        self.assertIsNone(create_ai_provider("grok"))

    def test_unknown_provider_is_rejected(self):
        with self.assertRaises(ValueError):
            create_ai_provider("mystery-provider")

    def test_gemini_provider_exposes_image_capability_boundary(self):
        provider = create_ai_provider("gemini", gemini_api_key="test-key")
        self.assertEqual(provider.name, "gemini")
        self.assertFalse(provider.supports_image_generation)


class ImageCapabilityTests(unittest.IsolatedAsyncioTestCase):
    async def test_unimplemented_image_generation_is_explicit(self):
        provider = create_ai_provider("gemini", gemini_api_key="test-key")
        with self.assertRaises(ImageGenerationUnavailable):
            await provider.generate_image(model="future-image-model", prompt="A lighthouse")
        await provider.close()


if __name__ == "__main__":
    unittest.main()
