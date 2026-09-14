The **Core Pro** update adds proactive raid and compromised-account defense to Keryx while preserving the moderation and modmail tools introduced in Core and Core+.

### 🍯 New Feature

#### 🛡️ Honeypot Auto-Ban

  * **Function:** Watches a configured security channel and automatically bans any non-exempt member who posts a message, attachment, sticker, or link.
  * **Cleanup:** Removes up to seven days of the banned member's messages, the maximum window supported by Discord's ban API.
  * **Audit Trail:** Records the triggering member, message, channel, message ID, and the explicit `Keryx Honeypot Auto-Ban` reason in a private staff log channel.
  * **Appeals:** Sends a private pre-ban DM containing the configured appeal-server link. The ban still proceeds when the member has DMs disabled.

#### ⚠️ Warning Embed (`/honeypot-warning`)

  * **Function:** Lets authorized staff post a clear security warning directly in the configured honeypot channel.
  * **Privacy:** The public warning does not expose the private appeal-server invite.

### 🔒 Safety & Reliability

  * **Staff Exemptions:** The server owner, administrators, and members with Manage Server or Moderate Members permissions cannot trigger the trap.
  * **Loop Protection:** Bot and webhook messages are ignored.
  * **Failure Reporting:** Failed bans and undeliverable appeal DMs are surfaced in the staff log instead of failing silently.
  * **Detain Reliability:** The existing `/detain` role changes now use shared validation for the Prison role and bot hierarchy.

### ⚙️ Configuration

  * Added `HONEYPOT_CHANNEL_ID` for the monitored channel.
  * Added `HONEYPOT_LOG_CHANNEL_ID` for private incident logs.
  * Added `APPEAL_SERVER_URL` for the private appeal notice.
  * Added `.env.example` and a setup README for easier deployments.

-----

**Full Changelog:** https://github.com/KodaNajimi42/Project-Keryx/compare/1.1.0...1.2.0
