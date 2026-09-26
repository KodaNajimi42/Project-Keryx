The **Keryx AI Lite** update brings controlled, free-tier-friendly Gemini text assistance to the server while preserving every moderation, honeypot, and modmail feature from Keryx Core Pro.

### 🤖 New Feature

#### 💬 Ask Keryx (`/ask`)

  * **Function:** Members can ask Keryx a question and receive a concise Gemini-powered response directly in Discord.
  * **Dedicated Channel:** `/ask` only operates in the channel configured with `AI_CHANNEL_ID`.
  * **Optional Role Access:** Staff can allow everyone or restrict AI access to one configured Discord role.
  * **Discord-Safe Output:** Long answers are split cleanly and generated mentions cannot ping members, roles, `@everyone`, or `@here`.

### 🛡️ Usage Controls & Safety

  * **Daily Quotas:** Persistent SQLite-backed per-user limits survive bot restarts and reset each UTC day.
  * **Cooldowns:** Per-user cooldowns reduce spam and protect the Gemini free-tier quota.
  * **Bounded Requests:** Questions are limited to 1,000 characters and response tokens are configurable.
  * **No Bot Authority:** The selected AI provider receives no tools and cannot run moderation commands or alter Discord state.
  * **Safety Handling:** Blocked, empty, rate-limited, and failed responses produce clear user-facing errors without consuming daily quota.

### 📋 Staff Visibility

  * **Private Logs:** Questions, answers, user IDs, model names, and remaining daily allowance are recorded in `AI_LOG_CHANNEL_ID`.
  * **Service Diagnostics:** Gemini API failures are written to the Keryx service log without exposing the API key.

### ⚙️ Configuration

  * Added `GEMINI_API_KEY`, `AI_CHANNEL_ID`, and `AI_LOG_CHANNEL_ID`.
  * Added configurable model, role access, cooldown, daily limit, output limit, and quota database path.
  * Added a vendor-neutral provider layer supporting Gemini, OpenAI, Grok/xAI, and custom OpenAI-compatible endpoints.
  * Added an editable `keryx_personality.txt` file while preserving non-negotiable safety boundaries in code.
  * Reserved an image-generation provider capability for a future `/imagine` update.
  * Added the official `google-genai` and OpenAI Python SDKs plus automated tests for providers, quotas, and Discord message splitting.

-----

**Full Changelog:** https://github.com/KodaNajimi42/Project-Keryx/compare/1.2.0...2.0.0
