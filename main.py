import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

# --- CONFIGURATION SECTION ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# We use int() because .env values are strings by default
STAFF_GUILD_ID = int(os.getenv('STAFF_GUILD_ID'))
MODMAIL_CATEGORY_ID = int(os.getenv('MODMAIL_CATEGORY_ID'))
MAIN_GUILD_ID = int(os.getenv('MAIN_GUILD_ID'))
PRISON_ROLE_ID = int(os.getenv('PRISON_ROLE_ID'))
# -----------------------------

class Client(commands.Bot):
    def __init__(self):
        # Intents are required for role management and message reading
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # Sync slash commands to the Main Server instantly
        self.tree.copy_global_to(guild=discord.Object(id=MAIN_GUILD_ID))
        await self.tree.sync(guild=discord.Object(id=MAIN_GUILD_ID))
        print("✅ Slash commands synced!")

client = Client()

@client.event
async def on_ready():
    print(f'🔥 Project Keryx is active: {client.user}')

# --- SLASH COMMAND: PING ---
@client.tree.command(name="ping", description="Check latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f'🏓 Pong! {round(client.latency * 1000)}ms')


# --- SLASH COMMAND: PRISON (Wipe Roles) ---
@client.tree.command(name="prison", description="Wipe ALL roles and imprison user")
@app_commands.checks.has_permissions(manage_roles=True)
async def prison(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer() # Operation might take a moment

    prison_role = interaction.guild.get_role(PRISON_ROLE_ID)
    
    if not prison_role:
        await interaction.followup.send("❌ Critical Error: Prison Role ID is invalid.")
        return

    # LOGIC: We cannot remove @everyone or 'managed' roles (like Server Booster or Bot roles).
    # So we build a list of roles to KEEP, then add the Prison role to it.
    roles_to_keep = [role for role in member.roles if role.managed or role.is_default()]
    roles_to_keep.append(prison_role)

    try:
        # discord.py handles the "wipe and replace" in one API call using edit()
        await member.edit(roles=roles_to_keep, reason=f"Imprisoned by {interaction.user.name}")
        await interaction.followup.send(f"🚨 **{member.display_name}** has been stripped of all roles and imprisoned.")
    
    except discord.Forbidden:
        await interaction.followup.send("❌ Error: I don't have permission. Is my bot role HIGHER than the user's current roles?")
    except Exception as e:
        await interaction.followup.send(f"❌ Unknown Error: {e}")


# --- MODMAIL SYSTEM (Category Based) ---
@client.event
async def on_message(message):
    # Ignore bot messages
    if message.author.bot:
        return

    # CASE 1: User DMs the Bot (New Ticket or Reply)
    if isinstance(message.channel, discord.DMChannel):
        staff_guild = client.get_guild(STAFF_GUILD_ID)
        category = staff_guild.get_channel(MODMAIL_CATEGORY_ID)
        
        if not category:
            print("❌ Modmail Category ID is invalid.")
            return

        # Check if a channel for this user already exists
        # We search for a channel named after their ID or Name
        channel_name = f"mail-{message.author.name.lower().replace(' ', '-')}"
        
        # Look for existing channel in the category
        mail_channel = discord.utils.get(category.text_channels, name=channel_name)

        if not mail_channel:
            # Create new channel if it doesn't exist
            overwrites = {
                staff_guild.default_role: discord.PermissionOverwrite(read_messages=False),
                staff_guild.me: discord.PermissionOverwrite(read_messages=True)
                # You can add specific mod roles here if you want
            }
            mail_channel = await staff_guild.create_text_channel(
                name=channel_name,
                category=category,
                topic=f"User ID: {message.author.id}"
            )
            await mail_channel.send(f"@here 📩 **New Ticket Created** for {message.author.mention} (`{message.author.id}`)")

        # Send the user's message to the staff channel
        embed = discord.Embed(description=message.content, color=discord.Color.blue())
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        if message.attachments:
            embed.set_image(url=message.attachments[0].url)
        
        await mail_channel.send(embed=embed)
        await message.add_reaction("✅")

    # CASE 2: Staff replies in a Modmail Channel
    # We check if the message is in the Modmail Category
    elif message.channel.category and message.channel.category.id == MODMAIL_CATEGORY_ID:
        # We need to find who this channel belongs to.
        # We saved the User ID in the channel TOPIC when we created it.
        try:
            user_id = int(message.channel.topic.split(":")[-1].strip())
            user = client.get_user(user_id)
            if user:
                embed = discord.Embed(description=message.content, color=discord.Color.green())
                embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
                if message.attachments:
                    embed.set_image(url=message.attachments[0].url)

                await user.send(embed=embed)
                await message.add_reaction("📨")
            else:
                await message.channel.send("❌ Could not find user. Have they left the server?")
        except Exception:
            # This handles normal chatter in the category that isn't a reply
            pass

client.run(TOKEN)
