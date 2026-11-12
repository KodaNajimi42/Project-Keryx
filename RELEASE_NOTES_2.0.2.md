The **Keryx AI Lite 2.0.2** patch fixes a modmail ticket duplication issue so repeat DMs stay in the same staff conversation.

### 📬 Modmail Reliability

  * **One Ticket Per Member:** Keryx now finds modmail tickets by the member's permanent Discord user ID stored in the channel topic, rather than by their changeable username.
  * **Repeat DM Handling:** Later DMs from the same member reuse their existing ticket instead of opening another channel.
  * **Rapid-DM Protection:** A per-member lock prevents two nearly simultaneous DMs from racing into duplicate tickets.
  * **Stable New Ticket Names:** New channels use the member's Discord user ID in their name, avoiding username collisions.
  * **Existing History Preserved:** Old duplicate channels are left untouched for staff records; new messages go to that member's oldest matching ticket.

### 🧪 Quality

  * Added automated coverage for ticket lookup, invalid topics, username collisions, and duplicate-ticket selection.
  * Made quota-retention tests independent of the current date so they remain reliable over time.

-----

**Full Changelog:** https://github.com/KodaNajimi42/Project-Keryx/compare/2.0.1...2.0.2
