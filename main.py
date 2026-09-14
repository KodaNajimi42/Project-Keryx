import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

# --- CONFIGURATION SECTION ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Ensure these are set in your .env file
STAFF_GUILD_ID = int(os.getenv('STAFF_GUILD_ID'))
MODMAIL_CATEGORY_ID = int(os.getenv('MODMAIL_CATEGORY_ID'))
MAIN_GUILD_ID = int(os.getenv('MAIN_GUILD_ID'))
PRISON_ROLE_ID = int(os.getenv('PRISON_ROLE_ID'))
PERMS_ROLE_ID = int(os.getenv('PERMS_ROLE_ID'))
HONEYPOT_CHANNEL_ID = int(os.getenv('HONEYPOT_CHANNEL_ID'))
HONEYPOT_LOG_CHANNEL_ID = int(os.getenv('HONEYPOT_LOG_CHANNEL_ID'))
APPEAL_SERVER_URL = os.getenv('APPEAL_SERVER_URL', '').strip()

# Parse the comma-separated list of roles to remove for soft jail
soft_jail_roles_raw = os.getenv('SOFT_JAIL_REMOVE_ROLES', '')
SOFT_JAIL_REMOVE_ROLES = [int(r) for r in soft_jail_roles_raw.split(',')] if soft_jail_roles_raw else []
# -----------------------------

class Client(commands.Bot):
    def __init__(self):
        # Intents are required to read messages and manage members
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # Instantly syncs slash commands to your main server
        self.tree.copy_global_to(guild=discord.Object(id=MAIN_GUILD_ID))
        await self.tree.sync(guild=discord.Object(id=MAIN_GUILD_ID))
        print("✅ Keryx Core Pro Slash Commands Synced!")

client = Client()

@client.event
async def on_ready():
    print(f'🔥 Keryx is online and active as: {client.user}')

# --- HELPER: HIERARCHY CHECK ---
def check_hierarchy(interaction: discord.Interaction, member: discord.Member):
    """Ensures staff cannot target users higher than them, and the bot has permission."""
    # Guild owner overrides all
    if interaction.user.id == interaction.guild.owner_id:
        return True, ""
    
    # Check if the user outranks the target
    if interaction.user.top_role.position <= member.top_role.position:
        return False, "❌ You cannot use this command on someone who outranks you or has the same top role."
    
    # Check if the bot outranks the target
    if interaction.guild.me.top_role.position <= member.top_role.position:
        return False, "❌ I cannot modify this user's roles because their top role is higher than mine."
        
    return True, ""


def get_detention_roles(member: discord.Member):
    """Return configured soft-jail roles that the member currently has."""
    return [
        role
        for role_id in SOFT_JAIL_REMOVE_ROLES
        if (role := member.guild.get_role(role_id)) and role in member.roles
    ]


async def apply_detention(member: discord.Member, reason: str):
    """Remove configured access roles and apply the Prison role."""
    prison_role = member.guild.get_role(PRISON_ROLE_ID)
    if not prison_role:
        raise RuntimeError("The Prison Role ID is missing or invalid.")

    bot_member = member.guild.me
    if not bot_member or bot_member.top_role <= prison_role:
        raise RuntimeError("The Prison role is higher than or equal to my top role.")
    if bot_member.top_role <= member.top_role:
        raise RuntimeError("The member's top role is higher than or equal to my top role.")

    roles_to_remove = [
        role for role in get_detention_roles(member) if role < bot_member.top_role
    ]
    if roles_to_remove:
        await member.remove_roles(*roles_to_remove, reason=reason)
    await member.add_roles(prison_role, reason=reason)

    return roles_to_remove, prison_role


# --- COMMAND: PING ---
@client.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f'🏓 Pong! Latency: {round(client.latency * 1000)}ms')


# --- COMMAND: HONEYPOT WARNING ---
@client.tree.command(name="honeypot-warning", description="Post the honeypot security warning")
@app_commands.checks.has_permissions(manage_channels=True)
async def honeypot_warning(interaction: discord.Interaction):
    if interaction.channel_id != HONEYPOT_CHANNEL_ID:
        await interaction.response.send_message(
            "❌ This warning can only be posted in the configured honeypot channel.",
            ephemeral=True,
        )
        return

    embed = discord.Embed(
        title="⚠️ Security Notice",
        description=(
            "**Do not send messages, files, stickers, or links in this channel.**\n\n"
            "This channel is monitored by Keryx. Any member who posts here will "
            "be **automatically banned** from the server and their recent messages "
            "will be removed."
        ),
        color=discord.Color.red(),
    )
    embed.set_footer(text="If you need help, contact staff through the proper support channel.")
    await interaction.response.send_message(embed=embed)


# --- COMMAND: PERMS (Grant Access) ---
@client.tree.command(name="perms", description="Grant the official permissions role to a user")
@app_commands.checks.has_permissions(manage_roles=True)
async def perms(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer()
    
    perms_role = interaction.guild.get_role(PERMS_ROLE_ID)
    
    if not perms_role:
        await interaction.followup.send("❌ Error: The Perms Role ID is missing or invalid.")
        return

    # Check if the bot is allowed to give this specific role
    if interaction.guild.me.top_role.position <= perms_role.position:
        await interaction.followup.send("❌ I cannot assign this role because it is higher than my own top role.")
        return

    try:
        await member.add_roles(perms_role, reason=f"Perms granted by {interaction.user.name}")
        await interaction.followup.send(f"✅ Successfully granted the **{perms_role.name}** role to {member.mention}.")
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")


# --- COMMAND: DETAIN (Soft Jail) ---
@client.tree.command(name="detain", description="Remove specific access roles and temporarily detain user")
@app_commands.checks.has_permissions(manage_roles=True)
async def detain(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer()

    is_valid, error_msg = check_hierarchy(interaction, member)
    if not is_valid:
        await interaction.followup.send(error_msg)
        return

    try:
        await apply_detention(member, reason=f"Detained by {interaction.user} ({interaction.user.id})")
        await interaction.followup.send(f"🚔 **{member.display_name}** has been detained (Soft Jail).")
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")


# --- COMMAND: PRISON (Hard Jail) ---
@client.tree.command(name="prison", description="Wipe ALL roles and imprison user (Hard Jail)")
@app_commands.checks.has_permissions(manage_roles=True)
async def prison(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer()

    is_valid, error_msg = check_hierarchy(interaction, member)
    if not is_valid:
        await interaction.followup.send(error_msg)
        return

    prison_role = interaction.guild.get_role(PRISON_ROLE_ID)
    
    # Strip all roles EXCEPT default (@everyone) and managed integrations (boosters, other bots)
    roles_to_keep = [role for role in member.roles if role.managed or role.is_default()]
    roles_to_keep.append(prison_role)

    try:
        # Overwrite the user's roles entirely
        await member.edit(roles=roles_to_keep, reason=f"Hard Imprisoned by {interaction.user.name}")
        await interaction.followup.send(f"🚨 **{member.display_name}** has been stripped of all roles and hard-jailed.")
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")


# --- MODMAIL SYSTEM ---
@client.event
async def on_message(message):
    # Prevent bot loops
    if message.author.bot or message.webhook_id is not None:
        return

    # CASE 1: A member interacts with the honeypot channel
    if (
        message.guild
        and message.guild.id == MAIN_GUILD_ID
        and message.channel.id == HONEYPOT_CHANNEL_ID
        and isinstance(message.author, discord.Member)
    ):
        member = message.author
        exempt = (
            member.id == message.guild.owner_id
            or member.guild_permissions.administrator
            or member.guild_permissions.manage_guild
            or member.guild_permissions.moderate_members
        )
        if exempt:
            return

        log_channel = message.guild.get_channel(HONEYPOT_LOG_CHANNEL_ID)
        evidence = message.content or "[No text content]"
        evidence = evidence[:1000]
        ban_reason = (
            f"Keryx Honeypot Auto-Ban: message sent in #{message.channel} "
            f"(message ID: {message.id})"
        )
        dm_delivered = False

        try:
            appeal_text = (
                f"\n\nYou may appeal here: {APPEAL_SERVER_URL}"
                if APPEAL_SERVER_URL
                else ""
            )
            try:
                await member.send(
                    f"🚫 You were automatically banned from **{message.guild.name}** for "
                    f"posting in its honeypot security channel.{appeal_text}"
                )
                dm_delivered = True
            except (discord.Forbidden, discord.HTTPException):
                pass

            await member.ban(
                reason=ban_reason,
                delete_message_seconds=604800,
            )
            if log_channel:
                embed = discord.Embed(
                    title="🍯 Honeypot triggered",
                    description=f"{member.mention} was automatically banned.",
                    color=discord.Color.red(),
                )
                embed.add_field(name="Channel", value=message.channel.mention, inline=True)
                embed.add_field(name="Message ID", value=str(message.id), inline=True)
                embed.add_field(name="Message", value=evidence, inline=False)
                embed.add_field(name="Audit reason", value=ban_reason, inline=False)
                embed.add_field(
                    name="Appeal notice",
                    value="DM delivered" if dm_delivered else "DM could not be delivered",
                    inline=False,
                )
                embed.set_footer(text=f"User ID: {member.id}")
                await log_channel.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException, RuntimeError) as error:
            if log_channel:
                await log_channel.send(
                    f"⚠️ Honeypot triggered by {member.mention} (`{member.id}`), "
                    f"but the automatic ban failed: `{error}`"
                )
            else:
                print(
                    f"Honeypot ban failed for {member} ({member.id}): {error}"
                )
        return

    # CASE 2: User sends a Direct Message to the bot
    if isinstance(message.channel, discord.DMChannel):
        staff_guild = client.get_guild(STAFF_GUILD_ID)
        category = staff_guild.get_channel(MODMAIL_CATEGORY_ID)
        if not category: 
            return

        # Format channel name to match Discord's standard (lowercase, hyphens)
        channel_name = f"mail-{message.author.name.lower().replace(' ', '-')}"
        mail_channel = discord.utils.get(category.text_channels, name=channel_name)

        # Create the ticket channel if it doesn't exist
        if not mail_channel:
            mail_channel = await staff_guild.create_text_channel(
                name=channel_name, 
                category=category, 
                topic=f"User ID: {message.author.id}"
            )
            await mail_channel.send(f"@here 📩 **New Ticket** opened by {message.author.mention}")

        # Send the user's message as a clean embed
        embed = discord.Embed(description=message.content, color=discord.Color.blue())
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        if message.attachments: 
            embed.set_image(url=message.attachments[0].url)
        
        await mail_channel.send(embed=embed)
        await message.add_reaction("✅") # Confirm to user it was sent

    # CASE 3: Staff replies inside the Modmail Category
    elif message.channel.category and message.channel.category.id == MODMAIL_CATEGORY_ID:
        try:
            # Extract the user's ID from the channel topic
            user_id = int(message.channel.topic.split(":")[-1].strip())
            user = client.get_user(user_id)
            
            if user:
                # Forward staff reply to the user's DMs
                embed = discord.Embed(description=message.content, color=discord.Color.green())
                embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
                if message.attachments: 
                    embed.set_image(url=message.attachments[0].url)

                await user.send(embed=embed)
                await message.add_reaction("📨") # Confirm to staff it was sent
        except Exception:
            # Ignore messages that don't match the format or if user left
            pass

client.run(TOKEN)
