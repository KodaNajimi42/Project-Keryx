# Project Keryx

Keryx AI Lite is a Discord moderation, utility, and community-assistance bot. It combines manual jail tools, a two-way modmail relay, predefined role assignment, an automated honeypot defense, and a controlled Gemini-powered `/ask` command.

## Features

- `/prison` removes all removable roles and applies the configured Prison role.
- `/detain` removes selected access roles and applies the Prison role.
- `/perms` grants the configured permissions role.
- `/honeypot-warning` posts the public warning in the configured honeypot channel.
- Direct messages to Keryx open private modmail channels for staff replies.
- Messages in the honeypot channel trigger an automatic ban, staff log, seven-day message cleanup, and best-effort appeal DM.
- `/ask` provides concise Gemini answers in one dedicated channel with persistent daily quotas and per-user cooldowns.

## Requirements

- Python 3.10 or newer
- A Discord application and bot token
- A Gemini API key from Google AI Studio
- Server-side Member and Message Content privileged intents enabled in the Discord Developer Portal
- A Linux host if you want to use the included systemd service template

Keryx needs View Channels, Send Messages, Read Message History, Manage Roles, Manage Channels, and Ban Members permissions. Place its highest role above the Prison role and every member or role it needs to manage.

## Getting started

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/KodaNajimi42/Project-Keryx.git
cd Project-Keryx
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy the configuration template and replace every placeholder with your own values:

```bash
cp .env.example .env
```

Never commit `.env`; it contains your Discord token and deployment-specific configuration.

Start the bot locally:

```bash
python main.py
```

For a persistent Ubuntu deployment, copy `service.example` to `/etc/systemd/system/keryx.service`, replace the example user and paths, then enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now keryx
sudo systemctl status keryx --no-pager -l
```

## Honeypot setup

1. Create a visible channel such as `#do-not-use` and a private staff channel such as `#honeypot-logs`.
2. Put both channel IDs and a permanent appeal-server invite in `.env`.
3. Restart Keryx and run `/honeypot-warning` inside the honeypot channel.
4. Test with a disposable non-staff account before announcing the feature.

Discord only allows the ban operation to remove messages from the previous seven days. Keryx cannot erase a member's complete lifetime message history through that operation.

## AI Lite setup

1. Create a Gemini API key in [Google AI Studio](https://aistudio.google.com/apikey).
2. Create a public AI channel such as `#ask-keryx` and a private staff log channel such as `#ai-logs`.
3. Add the API key, both channel IDs, and your desired limits to `.env` using `.env.example` as a guide.
4. Set `AI_ALLOWED_ROLE_ID=0` to let every member use `/ask`, or set it to one role ID to restrict access.
5. Install the updated requirements and restart Keryx.

```bash
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart keryx
```

AI usage is stored in `keryx_ai_usage.db`, so daily quotas survive restarts. Requests reset by UTC date, and counters older than `AI_USAGE_RETENTION_DAYS` are deleted automatically. Free-tier Gemini prompts and responses may be used by Google to improve its products; do not send private modmail, staff discussions, credentials, or personal information through `/ask`.

### Providers and models

The Discord command talks to a vendor-neutral provider layer. Change providers and models through `.env` without modifying the bot:

```dotenv
# Gemini
AI_PROVIDER=gemini
AI_MODEL=gemini-3.1-flash-lite
GEMINI_API_KEY=your_key

# OpenAI
AI_PROVIDER=openai
AI_MODEL=your_openai_model_id
OPENAI_API_KEY=your_key

# Grok / xAI
AI_PROVIDER=grok
AI_MODEL=grok-4.7
XAI_API_KEY=your_key
```

An `openai-compatible` option is also available through `AI_API_KEY` and `AI_BASE_URL`. Only the key for the selected provider is required. Provider pricing, privacy, safety, and rate limits still apply.

### Personality

Edit `keryx_personality.txt` to change Keryx's tone and character, then restart the service. The separate safety boundary remains enforced in code. The provider interface also reserves an image-generation method so a future `/imagine` command can be added without redesigning `/ask`.

## Credits

Project Keryx is created and maintained by [KodaNajimi42](https://github.com/KodaNajimi42). Development and documentation were assisted by Google Gemini and OpenAI Codex.

## Legal

- [Terms of Service](https://kodanajimi42.github.io/Project-Keryx/terms.html)
- [Privacy Policy](https://kodanajimi42.github.io/Project-Keryx/privacy.html)

## License

This project is available under the [MIT License](LICENSE).
