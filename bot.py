import discord
from discord.ext import commands
import json
import os
import asyncio
import random

# ===== CONFIG =====
CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({}, f)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

config = load_config()

# ===== BOT SETUP =====
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ===== EVENTS =====
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"⚠️ Slash sync failed: {e}")
    print(f"🤖 Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    guild_conf = config.get(str(member.guild.id), {})
    guild = member.guild
    if guild_conf.get('welcome'):
        channel = guild.get_channel(guild_conf['welcome'])
        if channel:
            embed = discord.Embed(
                title="🎉 Welcome!",
                description=f"Hey {member.mention}, welcome to **{guild.name}**!",
                color=discord.Color.green()
            )
            embed.add_field(name="👥 Member Count", value=f"{guild.member_count}", inline=True)
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            await channel.send(embed=embed)
    if "autorole" in guild_conf:
        role = guild.get_role(guild_conf["autorole"])
        if role:
            await member.add_roles(role)

# ===== HELP FUNCTION =====
async def send_help(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 Bot Commands", color=discord.Color.blue())
    embed.add_field(
        name="General",
        value="`avatar`, `ping`, `say`, `userinfo`, `serverinfo`, `membercount`",
        inline=False,
    )
    embed.add_field(
        name="Moderation",
        value="`kick`, `ban`, `unban`, `mute`, `unmute`, `clear`",
        inline=False,
    )
    embed.add_field(
        name="Utility",
        value="`announcement`, `setwelcome`, `setlog`, `setautorole`, `giveaway`",
        inline=False,
    )
    await interaction.response.send_message(embed=embed)

# ===== SLASH COMMANDS =====
# 1️⃣ Help
@bot.tree.command(name="helpme", description="Show bot commands")
async def helpme(interaction: discord.Interaction):
    await send_help(interaction)

# 2️⃣ Ping
@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! {round(bot.latency*1000)}ms")

# 3️⃣ Say
@bot.tree.command(name="say", description="Make the bot say something")
async def say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

# 4️⃣ Avatar
@bot.tree.command(name="avatar", description="Show a user's avatar")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"{member.display_name}'s Avatar")
    embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
    await interaction.response.send_message(embed=embed)

# 5️⃣ Userinfo
@bot.tree.command(name="userinfo", description="Show user information")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"User Info - {member}", color=discord.Color.green())
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"), inline=False)
    embed.add_field(name="Created", value=member.created_at.strftime("%Y-%m-%d"), inline=False)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    await interaction.response.send_message(embed=embed)

# 6️⃣ Serverinfo
@bot.tree.command(name="serverinfo", description="Show server information")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"{guild.name} Info", color=discord.Color.orange())
    embed.add_field(name="Owner", value=guild.owner, inline=False)
    embed.add_field(name="Members", value=guild.member_count, inline=False)
    embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=False)
    await interaction.response.send_message(embed=embed)

# 7️⃣ Membercount
@bot.tree.command(name="membercount", description="Show member count")
async def membercount(interaction: discord.Interaction):
    await interaction.response.send_message(f"👥 Members: {interaction.guild.member_count}")

# 8️⃣ Kick
@bot.tree.command(name="kick", description="Kick a member")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ You don't have permission to kick members.", ephemeral=True)
    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 Kicked {member} for: {reason}")

# 9️⃣ Ban
@bot.tree.command(name="ban", description="Ban a member")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ You don't have permission to ban members.", ephemeral=True)
    await member.ban(reason=reason)
    await interaction.response.send_message(f"🔨 Banned {member} for: {reason}")

# 🔟 Unban
@bot.tree.command(name="unban", description="Unban a member")
async def unban(interaction: discord.Interaction, user: str):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ You don't have permission to unban members.", ephemeral=True)
    banned_users = await interaction.guild.bans()
    for ban_entry in banned_users:
        if str(ban_entry.user) == user:
            await interaction.guild.unban(ban_entry.user)
            return await interaction.response.send_message(f"✅ Unbanned {ban_entry.user}")
    await interaction.response.send_message("❌ User not found.")

# 11️⃣ Clear
@bot.tree.command(name="clear", description="Clear messages")
async def clear(interaction: discord.Interaction, amount: int = 5):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message(
            "❌ You don't have permission to manage messages.", ephemeral=True
        )
    
    # Defer the response to prevent timeout
    await interaction.response.defer(ephemeral=True)

    # Purge messages
    deleted = await interaction.channel.purge(limit=amount)
    
    # Send follow-up message
    await interaction.followup.send(f"🧹 Cleared {len(deleted)} messages.", ephemeral=True)

# 12️⃣ Mute
@bot.tree.command(name="mute", description="Mute a member")
async def mute(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message("❌ You don't have permission to mute members.", ephemeral=True)
    role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not role:
        role = await interaction.guild.create_role(name="Muted")
        for channel in interaction.guild.channels:
            await channel.set_permissions(role, speak=False, send_messages=False)
    await member.add_roles(role)
    await interaction.response.send_message(f"🔇 Muted {member}")

# 13️⃣ Unmute
@bot.tree.command(name="unmute", description="Unmute a member")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message("❌ You don't have permission to unmute members.", ephemeral=True)
    role = discord.utils.get(interaction.guild.roles, name="Muted")
    await member.remove_roles(role)
    await interaction.response.send_message(f"🔊 Unmuted {member}")

# 14️⃣ Announcement
@bot.tree.command(name="announcement", description="Make an announcement")
async def announcement(interaction: discord.Interaction, msg: str):
    embed = discord.Embed(title="📢 Announcement", description=msg, color=discord.Color.gold())
    await interaction.response.send_message(embed=embed)

# 15️⃣ Setwelcome
@bot.tree.command(name="setwelcome", description="Set welcome channel")
async def setwelcome(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.manage_guild:
        return await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
    config[str(interaction.guild.id)] = config.get(str(interaction.guild.id), {})
    config[str(interaction.guild.id)]["welcome"] = channel.id
    save_config(config)
    await interaction.response.send_message(f"✅ Welcome channel set to {channel.mention}")

# 16️⃣ Setlog
@bot.tree.command(name="setlog", description="Set log channel")
async def setlog(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.manage_guild:
        return await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
    config[str(interaction.guild.id)] = config.get(str(interaction.guild.id), {})
    config[str(interaction.guild.id)]["log"] = channel.id
    save_config(config)
    await interaction.response.send_message(f"✅ Log channel set to {channel.mention}")

# 17️⃣ Setautorole
@bot.tree.command(name="setautorole", description="Set autorole")
async def setautorole(interaction: discord.Interaction, role: discord.Role):
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
    config[str(interaction.guild.id)] = config.get(str(interaction.guild.id), {})
    config[str(interaction.guild.id)]["autorole"] = role.id
    save_config(config)
    await interaction.response.send_message(f"✅ Autorole set to {role.name}")

# 18️⃣ Automatic Giveaway
@bot.tree.command(name="giveaway", description="Start an automatic giveaway")
async def giveaway(interaction: discord.Interaction, prize: str, winners: int, duration: int):
    """prize: giveaway prize, winners: number of winners, duration: seconds"""
    if not interaction.user.guild_permissions.manage_guild:
        return await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)

    embed = discord.Embed(
        title="🎁 Giveaway!",
        description=f"Prize: **{prize}**\nReact with 🎉 to enter!\nTime: {duration} seconds\nNumber of winners: {winners}",
        color=discord.Color.purple()
    )
    embed.set_footer(text=f"Hosted by {interaction.user.display_name}")
    message = await interaction.channel.send(embed=embed)
    await message.add_reaction("🎉")
    await interaction.response.send_message(f"✅ Giveaway started for **{prize}**! React with 🎉", ephemeral=True)

    await asyncio.sleep(duration)

    message = await interaction.channel.fetch_message(message.id)
    users = set()
    for reaction in message.reactions:
        if str(reaction.emoji) == "🎉":
            async for user in reaction.users():
                if not user.bot:
                    users.add(user)
    if not users:
        await interaction.channel.send("❌ No one participated in the giveaway.")
        return

    winners_list = random.sample(list(users), k=min(winners, len(users)))
    winner_mentions = ", ".join([winner.mention for winner in winners_list])
    await interaction.channel.send(f"🏆 Congratulations {winner_mentions}! You won **{prize}**!")

# ===== START BOT =====
if __name__ == "__main__":
    token = input("🤖 Enter your bot token: ")
    bot.run(token)
