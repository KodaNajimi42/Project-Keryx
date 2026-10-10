The **Keryx AI Lite 2.0.1** patch adds the public policies needed for Discord app verification, improves Keryx's identity responses, and gives locally stored AI quota data a clear retention period.

### 📜 Public Policies

  * **Terms of Service:** Added a public Terms of Service page covering acceptable use, moderation, AI limitations, availability, and third-party services.
  * **Privacy Policy:** Added a public Privacy Policy explaining what Keryx processes, why it is processed, how it is shared, and how long it is retained.
  * **GitHub Pages Ready:** Added a responsive policy site in `docs/` for deployment through GitHub Pages.
  * **README Links:** Added direct links to both policies for server owners and Discord reviewers.

### 🤖 Keryx Identity

  * **Accurate Version:** Keryx now identifies itself as version 2.0.1 when asked.
  * **Runtime Model Details:** Keryx receives its active provider and model identifier at runtime, keeping identity answers accurate when providers are changed.
  * **Birthday:** Keryx recognizes the original 2.0.0 GitHub publication time as its birthday.

### 🛡️ Privacy & Retention

  * **Automatic Cleanup:** AI quota counters older than 30 days are deleted automatically by default.
  * **Configurable Retention:** Server owners can adjust the cleanup period with `AI_USAGE_RETENTION_DAYS`.
  * **Test Coverage:** Added an automated test confirming expired quota records are removed.

-----

**Full Changelog:** https://github.com/KodaNajimi42/Project-Keryx/compare/2.0.0...2.0.1
