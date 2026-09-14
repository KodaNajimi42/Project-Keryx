# Project Keryx

Keryx Core Pro is a focused Discord moderation and utility bot. It combines manual jail tools, a two-way modmail relay, predefined role assignment, and an automated honeypot defense.

## Features

- `/prison` removes all removable roles and applies the configured Prison role.
- `/detain` removes selected access roles and applies the Prison role.
- `/perms` grants the configured permissions role.
- `/honeypot-warning` posts the public warning in the configured honeypot channel.
- Direct messages to Keryx open private modmail channels for staff replies.
- Messages in the honeypot channel trigger an automatic ban, staff log, seven-day message cleanup, and best-effort appeal DM.

## Requirements

- Python 3.10 or newer
- A Discord application and bot token
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

## Credits

Project Keryx is created and maintained by [KodaNajimi42](https://github.com/KodaNajimi42). Development and documentation were assisted by Google Gemini and OpenAI Codex.

## License

This project is available under the [MIT License](LICENSE).
