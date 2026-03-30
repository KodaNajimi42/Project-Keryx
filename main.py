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
        print("✅ Keryx Core+ Slash Commands Synced!")

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


# --- COMMAND: PING ---
@client.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f'🏓 Pong! Latency: {round(client.latency * 1000)}ms')


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

    prison_role = interaction.guild.get_role(PRISON_ROLE_ID)
    roles_to_remove = [interaction.guild.get_role(role_id) for role_id in SOFT_JAIL_REMOVE_ROLES if interaction.guild.get_role(role_id)]

    try:
        # Remove only the specified roles if the user currently holds them
        for role in roles_to_remove:
            if role in member.roles:
                await member.remove_roles(role, reason=f"Detained by {interaction.user.name}")
        
        # Add the prison role
        await member.add_roles(prison_role, reason=f"Detained by {interaction.user.name}")
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
    if message.author.bot: 
        return

    # CASE 1: User sends a Direct Message to the bot
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

    # CASE 2: Staff replies inside the Modmail Category
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
