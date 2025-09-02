import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
import datetime
import os
import sys
from collections import defaultdict
import re

# Function to display a stylish banner
def display_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    ███████╗ █████╗ ██╗      ██████╗  ██████╗ ███╗   ██╗     ║
    ║    ██╔════╝██╔══██╗██║     ██╔═══██╗██╔═══██╗████╗  ██║     ║
    ║    █████╗  ███████║██║     ██║   ██║██║   ██║██╔██╗ ██║     ║
    ║    ██╔══╝  ██╔══██║██║     ██║   ██║██║   ██║██║╚██╗██║     ║
    ║    ██║     ██║  ██║███████╗╚██████╔╝╚██████╔╝██║ ╚████║     ║
    ║    ╚═╝     ╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝     ║
    ║                                                              ║
    ║                  ██████╗ ██████╗ ████████╗                  ║
    ║                 ██╔═══██╗██╔══██╗╚══██╔══╝                  ║
    ║                 ██║   ██║██████╔╝   ██║                     ║
    ║                 ██║   ██║██╔═══╝    ██║                     ║
    ║                 ╚██████╔╝██║        ██║                     ║
    ║                  ╚═════╝ ╚═╝        ╚═╝                     ║
    ║                                                              ║
    ║                     MADE BY AAYUSH                          ║
    ║                  🔥 FALCON DISCORD BOT 🔥                   ║
    ║              💎 Premium Quality Bot System 💎               ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

# Function to get bot token from user input
def get_token():
    display_banner()
    print("\n" + "="*60)
    print("🔐 BOT SETUP - Please enter your Discord bot token")
    print("="*60)
    print("💡 Get your token from: https://discord.com/developers/applications")
    
    token = input("\n🎯 Please enter your bot token: ").strip()
    
    if not token:
        print("❌ No token provided. Exiting...")
        sys.exit(1)
    
    return token

# Bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='-', intents=intents)

# Data storage
invite_data = {}
member_join_data = {}
server_config = {}
muted_users = {}

# Load data from file
def load_data():
    global invite_data, member_join_data, server_config, muted_users
    try:
        with open('falcon_data.json', 'r') as f:
            data = json.load(f)
            invite_data = data.get('invite_data', {})
            member_join_data = data.get('member_join_data', {})
            server_config = data.get('server_config', {})
            muted_users = data.get('muted_users', {})
    except FileNotFoundError:
        # Initialize with empty data
        invite_data = {}
        member_join_data = {}
        server_config = {}
        muted_users = {}

# Save data to file
def save_data():
    data = {
        'invite_data': invite_data,
        'member_join_data': member_join_data,
        'server_config': server_config,
        'muted_users': muted_users
    }
    with open('falcon_data.json', 'w') as f:
        json.dump(data, f, indent=4)

# Initialize data
load_data()

    # Send welcome message if configured
    if server_config[guild_id].get('welcome_channel'):
        channel = bot.get_channel(server_config[guild_id]['welcome_channel'])
        if channel:
            embed = discord.Embed(
                title="🎉 Welcome!",
                description=f"Hey {member.mention}, welcome to **{guild.name}**!",
                color=discord.Color.green()
            )
            if used_invite and inviter:
                embed.add_field(name="📬 Invited by", value=inviter.mention, inline=True)
                embed.add_field(name="🔗 Invite Code", value=used_invite.code, inline=True)
            embed.add_field(name="👥 Member Count", value=f"{guild.member_count}", inline=True)
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            await channel.send(embed=embed)

    # Assign auto role if configured
    try:
        if server_config[guild_id].get('auto_role'):
            role = guild.get_role(server_config[guild_id]['auto_role'])
            if role:
                await member.add_roles(role)
    except discord.Forbidden:
        print(f"⚠️ Missing permissions to assign role in {guild.name}")

    # Save data at the end
    save_data()


# Help command
@bot.command(name='helpme')
async def help_cmd(ctx):
    embed = discord.Embed(
        title="🤖 Falcon Bot Help",
        description="A powerful moderation and invite tracking bot made by Aayush",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📋 Information",
        value="`-si` or `/serverinfo` - Server information\n`-userinfo @user` - User information\n`-avatar @user` - Get user's avatar\n`-membercount` - Show member count",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Configuration",
        value="`-setlog #channel` - Set log channel\n`-setwelcome #channel` - Set welcome channel\n`-setautorole @role` - Set auto role\n`-config` - Show current config",
        inline=False
    )
    
    embed.add_field(
        name="🎉 Fun Commands",
        value="`-ping` - Check bot latency\n`-say [message]` - Make bot say something\n`-embed [title] [description]` - Create embed",
        inline=False
    )
    
    embed.set_footer(text="Made By Aayush | Use slash commands for easier usage!")
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    await ctx.send(embed=embed)


# Server info command
@bot.command(name='serverinfo', aliases=['si'])
async def server_info(ctx):
    guild = ctx.guild
    embed = discord.Embed(
        title=f"📋 {guild.name}",
        color=discord.Color.gold()
    )
    
    # Basic info
    embed.add_field(name="👑 Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="👥 Members", value=guild.member_count, inline=True)
    embed.add_field(name="🎭 Roles", value=len(guild.roles), inline=True)
    
    # Channels
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    categories = len(guild.categories)
    embed.add_field(name="📺 Text Channels", value=text_channels, inline=True)
    embed.add_field(name="🔊 Voice Channels", value=voice_channels, inline=True)
    embed.add_field(name="📁 Categories", value=categories, inline=True)
    
    # Other info
    created_at = guild.created_at.strftime("%b %d, %Y")
    embed.add_field(name="📅 Created", value=created_at, inline=True)
    embed.add_field(name="🚀 Boost Level", value=f"Level {guild.premium_tier}", inline=True)
    embed.add_field(name="💎 Boosts", value=guild.premium_subscription_count, inline=True)
    
    # Server icon
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    embed.set_footer(text="Made By Aayush")
    await ctx.send(embed=embed)
# Slash command version of serverinfo
@bot.tree.command(name="serverinfo", description="Show information about this server")
async def server_info_slash(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(
        title=f"📋 {guild.name}",
        color=discord.Color.gold()
    )
    
    # Basic info
    embed.add_field(name="👑 Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="👥 Members", value=guild.member_count, inline=True)
    embed.add_field(name="🎭 Roles", value=len(guild.roles), inline=True)
    
    # Channels
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    categories = len(guild.categories)
    embed.add_field(name="📺 Text Channels", value=text_channels, inline=True)
    embed.add_field(name="🔊 Voice Channels", value=voice_channels, inline=True)
    embed.add_field(name="📁 Categories", value=categories, inline=True)
    
    # Other info
    created_at = guild.created_at.strftime("%b %d, %Y")
    embed.add_field(name="📅 Created", value=created_at, inline=True)
    embed.add_field(name="🚀 Boost Level", value=f"Level {guild.premium_tier}", inline=True)
    embed.add_field(name="💎 Boosts", value=guild.premium_subscription_count, inline=True)
    
    # Server icon
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    embed.set_footer(text="Made By Aayush")
    await interaction.response.send_message(embed=embed)

# User info command
@bot.command(name='userinfo', aliases=['ui'])
async def user_info(ctx, member: discord.Member = None):
    member = member or ctx.author
    guild = ctx.guild
    
    embed = discord.Embed(
        title=f"👤 {member.name}",
        color=member.color
    )
    
    # Basic info
    embed.add_field(name="🆔 User ID", value=member.id, inline=True)
    embed.add_field(name="📛 Nickname", value=member.nick or "None", inline=True)
    embed.add_field(name="🎨 Top Role", value=member.top_role.mention, inline=True)
    
    # Dates
    joined_at = member.joined_at.strftime("%b %d, %Y %H:%M") if member.joined_at else "Unknown"
    created_at = member.created_at.strftime("%b %d, %Y %H:%M")
    embed.add_field(name="📥 Joined Server", value=joined_at, inline=True)
    embed.add_field(name="📅 Account Created", value=created_at, inline=True)
    
    # Invites
    guild_id = str(guild.id)
    if guild_id in server_config and 'invites' in server_config[guild_id]:
        invite_count = server_config[guild_id]['invites'].get(str(member.id), 0)
        embed.add_field(name="📊 Invites", value=invite_count, inline=True)
    
    # Avatar
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    
    embed.set_footer(text="Made By Aayush")
    await ctx.send(embed=embed)

# Avatar command
@bot.command(name='avatar', aliases=['av'])
async def avatar_cmd(ctx, member: discord.Member = None):
    member = member or ctx.author
    
    embed = discord.Embed(
        title=f"🖼️ {member.name}'s Avatar",
        color=member.color
    )
    
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    embed.set_image(url=avatar_url)
    embed.add_field(name="🔗 Avatar URL", value=f"[Click Here]({avatar_url})", inline=False)
    embed.set_footer(text="Made By Aayush")
    
    await ctx.send(embed=embed)

# Member count command
@bot.command(name='membercount', aliases=['mc'])
async def member_count(ctx):
    guild = ctx.guild
    
    embed = discord.Embed(
        title="👥 Member Count",
        description=f"**{guild.name}** has **{guild.member_count}** members",
        color=discord.Color.green()
    )
    embed.set_footer(text="Made By Aayush")
    await ctx.send(embed=embed)
# Moderation command - kick
@bot.command(name='kick', aliases=['k'])
@commands.has_permissions(kick_members=True)
async def kick_cmd(ctx, member: discord.Member, *, reason="No reason provided"):
    if member == ctx.author:
        await ctx.send("❌ You cannot kick yourself!")
        return
    
    if member.top_role >= ctx.author.top_role:
        await ctx.send("❌ You cannot kick someone with equal or higher role!")
        return
    
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="👢 Member Kicked",
            description=f"{member.mention} has been kicked by {ctx.author.mention}",
            color=discord.Color.red()
        )
        embed.add_field(name="📝 Reason", value=reason, inline=False)
        embed.set_footer(text="Made By Aayush")
        await ctx.send(embed=embed)
    except discord.NotFound:
        await ctx.send("❌ User not found or not banned.")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to unban members.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

# Mute command
@bot.command(name='mute', aliases=['m'])
@commands.has_permissions(manage_roles=True)
async def mute_cmd(ctx, member: discord.Member, duration: str = "10m", *, reason="No reason provided"):
    if member == ctx.author:
        await ctx.send("❌ You cannot mute yourself!")
        return
    
    if member.top_role >= ctx.author.top_role:
        await ctx.send("❌ You cannot mute someone with equal or higher role!")
        return
    
    # Parse duration
    time_regex = re.compile(r"(\d+)([smhd])")
    match = time_regex.match(duration.lower())
    
    if not match:
        await ctx.send("❌ Invalid time format! Use: 10s, 5m, 1h, 1d")
        return
    
    amount, unit = match.groups()
    amount = int(amount)
    
    if unit == 's':
        seconds = amount
    elif unit == 'm':
        seconds = amount * 60
    elif unit == 'h':
        seconds = amount * 3600
    elif unit == 'd':
        seconds = amount * 86400
    
    # Create or get muted role
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        try:
            muted_role = await ctx.guild.create_role(name="Muted", color=discord.Color.dark_grey())
            # Set permissions for the role
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to create the Muted role.")
            return
    
    try:
        await member.add_roles(muted_role, reason=reason)
        
        # Store mute data
        guild_id = str(ctx.guild.id)
        if guild_id not in muted_users:
            muted_users[guild_id] = {}
        
        muted_users[guild_id][str(member.id)] = {
            'muted_until': (datetime.datetime.now() + datetime.timedelta(seconds=seconds)).isoformat(),
            'reason': reason,
            'muted_by': ctx.author.id
        }
        save_data()
        
        embed = discord.Embed(
            title="🔇 Member Muted",
            description=f"{member.mention} has been muted for {duration}",
            color=discord.Color.orange()
        )
        embed.add_field(name="📝 Reason", value=reason, inline=False)
        embed.add_field(name="⏰ Duration", value=duration, inline=True)
        embed.add_field(name="👮 Moderator", value=ctx.author.mention, inline=True)
        embed.set_footer(text="Made By Aayush")
        await ctx.send(embed=embed)
        
        # Auto unmute after duration
        await asyncio.sleep(seconds)
        if str(member.id) in muted_users.get(guild_id, {}):
            await member.remove_roles(muted_role, reason="Mute expired")
            del muted_users[guild_id][str(member.id)]
            save_data()
            
            # Send unmute notification
            try:
                unmute_embed = discord.Embed(
                    title="🔊 Auto Unmute",
                    description=f"{member.mention} has been automatically unmuted",
                    color=discord.Color.green()
                )
                unmute_embed.set_footer(text="Made By Aayush")
                await ctx.send(embed=unmute_embed)
            except:
                pass
        
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to mute this member.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

# Unmute command
@bot.command(name='unmute')
@commands.has_permissions(manage_roles=True)
async def unmute_cmd(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        await ctx.send("❌ No muted role found.")
        return
    
    if muted_role not in member.roles:
        await ctx.send("❌ This member is not muted.")
        return
    
    try:
        await member.remove_roles(muted_role, reason=f"Unmuted by {ctx.author}")
        
        # Remove from muted users data
        guild_id = str(ctx.guild.id)
        if guild_id in muted_users and str(member.id) in muted_users[guild_id]:
            del muted_users[guild_id][str(member.id)]
            save_data()
        
        embed = discord.Embed(
            title="🔊 Member Unmuted",
            description=f"{member.mention} has been unmuted by {ctx.author.mention}",
            color=discord.Color.green()
        )
        embed.set_footer(text="Made By Aayush")
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to unmute this member.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")
# Clear messages command
@bot.command(name='clear', aliases=['purge'])
@commands.has_permissions(manage_messages=True)
async def clear_cmd(ctx, amount: int = 10):
    if amount < 1 or amount > 100:
        await ctx.send("❌ Amount must be between 1 and 100.")
        return
    
    try:
        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include command message
        
        embed = discord.Embed(
            title="🗑️ Messages Cleared",
            description=f"Successfully deleted {len(deleted) - 1} messages",
            color=discord.Color.green()
        )
        embed.set_footer(text="Made By Aayush")
        
        # Send confirmation and delete after 3 seconds
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(3)
        await msg.delete()
        
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to delete messages.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

# Configuration commands
@bot.command(name='setlog')
@commands.has_permissions(administrator=True)
async def set_log_channel(ctx, channel: discord.TextChannel):
    guild_id = str(ctx.guild.id)
    
    if guild_id not in server_config:
        server_config[guild_id] = {}
    
    server_config[guild_id]['log_channel'] = channel.id
    save_data()
    
    embed = discord.Embed(
        title="⚙️ Log Channel Set",
        description=f"Log channel has been set to {channel.mention}",
        color=discord.Color.green()
    )
    embed.set_footer(text="Made By Aayush")
    await ctx.send(embed=embed)

@bot.command(name='setwelcome')
@commands.has_permissions(administrator=True)
async def set_welcome_channel(ctx, channel: discord.TextChannel):
    guild_id = str(ctx.guild.id)
    
    if guild_id not in server_config:
        server_config[guild_id] = {}
    
    server_config[guild_id]['welcome_channel'] = channel.id
    save_data()
    
    embed = discord.Embed(
        title="⚙️ Welcome Channel Set",
        description=f"Welcome channel has been set to {channel.mention}",
        color=discord.Color.green()
    )
    embed.set_footer(text="Made By Aayush")
    await ctx.send(embed=embed)

@bot.command(name='setautorole')
@commands.has_permissions(administrator=True)
async def set_auto_role(ctx, role: discord.Role):
    guild_id = str(ctx.guild.id)
    
    if guild_id not in server_config:
        server_config[guild_id] = {}
    
    server_config[guild_id]['auto_role'] = role.id
    save_data()
    
    embed = discord.Embed(
        title="⚙️ Auto Role Set",
        description=f"Auto role has been set to {role.mention}",
        color=discord.Color.green()
    )
    embed.set_footer(text="Made By Aayush")
    await ctx.send(embed=embed)

# Config command to show current settings
@bot.command(name='config')
@commands.has_permissions(administrator=True)
async def config_cmd(ctx):
    guild_id = str(ctx.guild.id)
    config = server_config.get(guild_id, {})
    
    embed = discord.Embed(
        title="⚙️ Server Configuration",
        color=discord.Color.blue()
    )
    
    # Log channel
    log_channel_id = config.get('log_channel')
    log_channel = bot.get_channel(log_channel_id) if log_channel_id else None
    embed.add_field(
        name="📝 Log Channel",
        value=log_channel.mention if log_channel else "Not set",
        inline=True
    )
    
    # Welcome channel
    welcome_channel_id = config.get('welcome_channel')
    welcome_channel = bot.get_channel(welcome_channel_id) if welcome_channel_id else None
    embed.add_field(
        name="👋 Welcome Channel",
        value=welcome_channel.mention if welcome_channel else "Not set",
        inline=True
    )
    
    # Auto role
    auto_role_id = config.get('auto_role')
    auto_role = ctx.guild.get_role(auto_role_id) if auto_role_id else None
    embed.add_field(
        name="🎭 Auto Role",
        value=auto_role.mention if auto_role else "Not set",
        inline=True
    )
    
    embed.set_footer(text="Made By Aayush")
    await ctx.send(embed=embed)

# Ping command
@bot.command(name='ping')
async def ping_cmd(ctx):
    latency = round(bot.latency * 1000)
    
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Bot latency: **{latency}ms**",
        color=discord.Color.green()
    )
    embed.set_footer(text="Made By Aayush")
    await ctx.send(embed=embed)

# Say command
@bot.command(name='say')
@commands.has_permissions(manage_messages=True)
async def say_cmd(ctx, *, message):
    await ctx.message.delete()
    await ctx.send(message)

# Embed command
@bot.command(name='embed')
@commands.has_permissions(manage_messages=True)
async def embed_cmd(ctx, title, *, description):
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.blue()
    )
    embed.set_footer(text="Made By Aayush")
    await ctx.message.delete()
    await ctx.send(embed=embed)
# Error handler for commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required argument.")
    elif isinstance(error, commands.CommandNotFound):
        return  # ignore unknown commands
    else:
        await ctx.send(f"❌ An error occurred: {error}")

# Guild join event - set up default config
@bot.event
async def on_guild_join(guild):
    guild_id = str(guild.id)
    if guild_id not in server_config:
        server_config[guild_id] = {
            'log_channel': None,
            'welcome_channel': None,
            'auto_role': None,
            'invites': {}
        }
        save_data()
    
    print(f"📥 Joined new guild: {guild.name} ({guild.id})")

# About command
@bot.command(name='about')
async def about_cmd(ctx):
    embed = discord.Embed(
        title="🤖 Falcon Bot",
        description="A multipurpose Discord bot with moderation and invite tracking features.",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="👤 Author", value="Aayush", inline=True)
    embed.add_field(name="⚙️ Version", value="1.0.0", inline=True)
    embed.add_field(name="📚 Library", value=f"discord.py {discord.__version__}", inline=True)
    embed.add_field(name="🌐 Servers", value=len(bot.guilds), inline=True)
    embed.add_field(name="👥 Users", value=sum(g.member_count for g in bot.guilds), inline=True)
    
    embed.set_footer(text="Made By Aayush")
    await ctx.send(embed=embed)

# Invite command (to invite the bot)
@bot.command(name='invite')
async def invite_cmd(ctx):
    client_id = bot.user.id
    url = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions=8&scope=bot%20applications.commands"
    
    embed = discord.Embed(
        title="🔗 Invite Falcon Bot",
        description="Click the link below to invite Falcon Bot to your server:",
        color=discord.Color.blue()
    )
    embed.add_field(name="👉 Invite Link", value=f"[Click Here]({url})", inline=False)
    embed.set_footer(text="Made By Aayush")
    
    await ctx.send(embed=embed)
# Ban command
@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban_cmd(ctx, member: discord.Member, *, reason="No reason provided"):
    if member == ctx.author:
        await ctx.send("❌ You cannot ban yourself!")
        return
    
    if member.top_role >= ctx.author.top_role:
        await ctx.send("❌ You cannot ban someone with equal or higher role!")
        return
    
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="🔨 Member Banned",
            description=f"{member.mention} has been banned by {ctx.author.mention}",
            color=discord.Color.red()
        )
        embed.add_field(name="📝 Reason", value=reason, inline=False)
        embed.set_footer(text="Made By Aayush")
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to ban this member.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

# Unban command
@bot.command(name='unban')
@commands.has_permissions(ban_members=True)
async def unban_cmd(ctx, user_id: int):
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        
        embed = discord.Embed(
            title="♻️ Member Unbanned",
            description=f"{user.mention} has been unbanned by {ctx.author.mention}",
            color=discord.Color.green()
        )
        embed.set_footer(text="Made By Aayush")
        await ctx.send(embed=embed)
    except discord.NotFound:
        await ctx.send("❌ User not found or not banned.")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to unban members.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

# Main entry point
if __name__ == "__main__":
    try:
        token = get_token()
        bot.run(token)
    except KeyboardInterrupt:
        save_data()
        print("💾 Data saved. Made By Aayush - Falcon Bot! 🔥")
        print("👋 Goodbye!")
