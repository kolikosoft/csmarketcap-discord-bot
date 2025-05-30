import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timezone
import traceback

# Import our modules
from config import *
from utils import *
from views import LanguageSelectionView, SimpleTicketView

# Bot setup with all intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents, help_command=None)

# Global instances for persistent views (will be created in on_ready)
language_view = None
english_ticket_view = None
russian_ticket_view = None

@bot.event
async def on_ready():
    """Bot startup event"""
    global language_view, english_ticket_view, russian_ticket_view
    
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot ID: {bot.user.id}')
    logger.info(f'Servers: {len(bot.guilds)}')
    
    # Create persistent views
    language_view = LanguageSelectionView()
    english_ticket_view = SimpleTicketView('english')
    russian_ticket_view = SimpleTicketView('russian')
    
    # Add persistent views
    bot.add_view(language_view)
    bot.add_view(english_ticket_view)
    bot.add_view(russian_ticket_view)
    
    # Start background tasks
    if not update_stats.is_running():
        update_stats.start()
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="CS2 Trading Community"
        ),
        status=discord.Status.online
    )
    
    logger.info("Bot is ready and running!")

@bot.event
async def on_member_join(member):
    """Handle new member joining"""
    try:
        guild = member.guild
        
        # Find language selection channel
        language_channel = discord.utils.get(guild.text_channels, name=CHANNELS['choose_language'])
        
        if language_channel:
            # Create welcome embed
            embed = create_embed(
                "🌐 Welcome to CSMarketCap!",
                f"Hello {member.mention}! Welcome to our CS2 skin trading community.\n\n"
                "**To get started:**\n"
                "1. Choose your language in the channel below\n"
                "2. Access your language-specific channels\n"
                "3. Read the guidelines and start trading!\n\n"
                f"**Language Selection:** {language_channel.mention}\n\n"
                "Happy trading! 🎮",
                color=COLORS['primary']
            )
            
            # Send DM to new member
            try:
                await member.send(embed=embed)
                logger.info(f"Sent welcome DM to {member.name}")
            except discord.Forbidden:
                logger.warning(f"Could not send DM to {member.name} - DMs disabled")
        
    except Exception as e:
        logger.error(f"Error handling member join: {e}")

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CheckFailure):
        # Admin check failed - message already sent in utils.py
        return
    elif isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = create_embed(
            "❌ Missing Argument",
            f"Missing required argument: `{error.param.name}`",
            color=COLORS['error']
        )
        await ctx.send(embed=embed)
    else:
        logger.error(f"Command error in {ctx.command}: {error}")
        embed = create_embed(
            "❌ Error",
            "An unexpected error occurred. Please try again or contact an administrator.",
            color=COLORS['error']
        )
        await ctx.send(embed=embed)

@tasks.loop(seconds=10)
async def update_stats():
    """Update server statistics every 10 seconds"""
    try:
        for guild in bot.guilds:
            total_members, online_members = get_member_count_stats(guild)
            
            # Find stat channels by checking each voice channel
            total_channel = None
            online_channel = None
            
            for channel in guild.voice_channels:
                if channel.name.startswith("📊 Total Members:"):
                    total_channel = channel
                elif channel.name.startswith("🟢 Online Members:"):
                    online_channel = channel
            
            # Update channel names
            if total_channel:
                new_name = CHANNELS['total_members'].format(total_members)
                if total_channel.name != new_name:
                    await total_channel.edit(name=new_name)
                    logger.info(f"Updated total members channel: {new_name}")
            
            if online_channel:
                new_name = CHANNELS['online_members'].format(online_members)
                if online_channel.name != new_name:
                    await online_channel.edit(name=new_name)
                    logger.info(f"Updated online members channel: {new_name}")
                    
    except Exception as e:
        logger.error(f"Error updating stats: {e}")

@update_stats.before_loop
async def before_update_stats():
    """Wait for bot to be ready before starting stats loop"""
    await bot.wait_until_ready()

# ADMIN-ONLY COMMANDS

@bot.command(name='fresh')
@is_admin()
async def fresh_setup(ctx):
    """Complete server wipe and recreation (ADMIN ONLY)"""
    embed = create_embed(
        "⚠️ DANGEROUS OPERATION",
        "This will **COMPLETELY WIPE** the server and recreate it from scratch.\n\n"
        "**This will delete:**\n"
        "• All channels\n"
        "• All roles (except protected)\n"
        "• All messages\n\n"
        "**Type `CONFIRM` within 30 seconds to proceed.**",
        color=COLORS['error']
    )
    await ctx.send(embed=embed)
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content == 'CONFIRM'
    
    try:
        await bot.wait_for('message', check=check, timeout=30.0)
    except asyncio.TimeoutError:
        embed = create_embed(
            "❌ Cancelled",
            "Fresh setup cancelled - no confirmation received.",
            color=COLORS['warning']
        )
        await ctx.send(embed=embed)
        return
    
    embed = create_embed(
        "🔄 Fresh Setup Starting",
        "Starting complete server wipe and recreation...\nThis may take several minutes.",
        color=COLORS['info']
    )
    await ctx.send(embed=embed)
    
    await perform_fresh_setup(ctx.guild)
    
    embed = create_embed(
        "✅ Fresh Setup Complete",
        "Server has been completely wiped and recreated!\n"
        "The CSMarketCap community is ready for action! 🎮",
        color=COLORS['success']
    )
    await ctx.send(embed=embed)

@bot.command(name='setup')
@is_admin()
async def setup_server(ctx):
    """Standard server setup (ADMIN ONLY)"""
    embed = create_embed(
        "🔄 Server Setup",
        "Starting server setup...\nThis may take a few minutes.",
        color=COLORS['info']
    )
    await ctx.send(embed=embed)
    
    await perform_server_setup(ctx.guild)
    
    embed = create_embed(
        "✅ Setup Complete",
        "Server setup completed successfully!\n"
        "CSMarketCap is ready for trading! 🎮",
        color=COLORS['success']
    )
    await ctx.send(embed=embed)

@bot.command(name='cleanup')
@is_admin()
async def cleanup_server(ctx):
    """Clean server without full recreation (ADMIN ONLY)"""
    embed = create_embed(
        "🧹 Server Cleanup",
        "Starting server cleanup...",
        color=COLORS['info']
    )
    await ctx.send(embed=embed)
    
    await perform_cleanup(ctx.guild)
    
    embed = create_embed(
        "✅ Cleanup Complete",
        "Server cleanup completed successfully!",
        color=COLORS['success']
    )
    await ctx.send(embed=embed)

@bot.command(name='language')
@is_admin()
async def manual_language_setup(ctx):
    """Manually setup language selection (ADMIN ONLY)"""
    # Find language channel
    language_channel = discord.utils.get(ctx.guild.text_channels, name=CHANNELS['choose_language'])
    
    if not language_channel:
        embed = create_embed(
            "❌ Error",
            "Language selection channel not found. Run `!setup` first.",
            color=COLORS['error']
        )
        await ctx.send(embed=embed)
        return
    
    await setup_language_selection_channel(language_channel)
    
    embed = create_embed(
        "✅ Language Setup Complete",
        f"Language selection has been set up in {language_channel.mention}",
        color=COLORS['success']
    )
    await ctx.send(embed=embed)

@bot.command(name='help')
@is_admin()
async def help_command(ctx):
    """Show bot commands (ADMIN ONLY)"""
    fields = [
        {
            'name': '🔄 Setup Commands',
            'value': '`!fresh` - Complete server wipe and recreation\n'
                    '`!setup` - Standard server setup\n'
                    '`!cleanup` - Clean server without recreation\n'
                    '`!language` - Setup language selection\n'
                    '`!refresh_support` - Refresh support channel buttons\n'
                    '`!clear_support` - Clear all support channel messages\n'
                    '`!reset_tickets` - Clear stuck active tickets\n'
                    '`!fix_bot_permissions` - Check and fix bot permissions\n'
                    '`!check_tickets` - Show active tickets status\n'
                    '`!clear_user_tickets <user_id>` - Clear tickets for specific user',
            'inline': False
        },
        {
            'name': '📊 Information Commands',
            'value': '`!info` - Bot information\n'
                    '`!stats` - Server statistics\n'
                    '`!help` - Show this help message',
            'inline': False
        },
        {
            'name': '⚠️ Important Notes',
            'value': '• All commands are **ADMIN ONLY**\n'
                    '• Use `!fresh` for complete server reset\n'
                    '• Use `!setup` for initial server setup\n'
                    '• Use `!refresh_support` to fix button issues\n'
                    '• Use `!reset_tickets` if tickets get stuck\n'
                    '• Bot automatically handles member joins',
            'inline': False
        }
    ]
    
    embed = create_embed(
        "🤖 CSMarketCap Bot Commands",
        "Complete command list for server administrators:",
        color=COLORS['primary'],
        fields=fields
    )
    
    await ctx.send(embed=embed)

@bot.command(name='info')
@is_admin()
async def bot_info(ctx):
    """Show bot information (ADMIN ONLY)"""
    fields = [
        {
            'name': '🤖 Bot Information',
            'value': f'**Name:** {bot.user.name}\n'
                    f'**ID:** {bot.user.id}\n'
                    f'**Version:** Discord.py {discord.__version__}\n'
                    f'**Uptime:** Online since bot start',
            'inline': False
        },
        {
            'name': '📊 Server Statistics',
            'value': f'**Servers:** {len(bot.guilds)}\n'
                    f'**Total Members:** {sum(guild.member_count for guild in bot.guilds)}\n'
                    f'**Ping:** {round(bot.latency * 1000)}ms',
            'inline': False
        },
        {
            'name': '🎯 Features',
            'value': '• Bilingual server setup (EN/RU)\n'
                    '• Language role management\n'
                    '• Support ticket system\n'
                    '• Live member statistics\n'
                    '• Admin-only command system',
            'inline': False
        }
    ]
    
    embed = create_embed(
        "ℹ️ Bot Information",
        "CSMarketCap Discord Bot for CS2 Trading Community",
        color=COLORS['info'],
        fields=fields
    )
    
    await ctx.send(embed=embed)

@bot.command(name='stats')
@is_admin()
async def server_stats(ctx):
    """Show server statistics (ADMIN ONLY)"""
    guild = ctx.guild
    total_members, online_members = get_member_count_stats(guild)
    
    # Count roles
    english_role = discord.utils.get(guild.roles, name=ROLES['english'])
    russian_role = discord.utils.get(guild.roles, name=ROLES['russian'])
    
    english_count = len(english_role.members) if english_role else 0
    russian_count = len(russian_role.members) if russian_role else 0
    
    fields = [
        {
            'name': '👥 Member Statistics',
            'value': f'**Total Members:** {total_members}\n'
                    f'**Online Members:** {online_members}\n'
                    f'**Offline Members:** {total_members - online_members}',
            'inline': True
        },
        {
            'name': '🌐 Language Distribution',
            'value': f'**English:** {english_count}\n'
                    f'**Russian:** {russian_count}\n'
                    f'**No Language:** {total_members - english_count - russian_count}',
            'inline': True
        },
        {
            'name': '📁 Server Structure',
            'value': f'**Categories:** {len(guild.categories)}\n'
                    f'**Text Channels:** {len(guild.text_channels)}\n'
                    f'**Voice Channels:** {len(guild.voice_channels)}',
            'inline': True
        }
    ]
    
    embed = create_embed(
        "📊 Server Statistics",
        f"Statistics for **{guild.name}**",
        color=COLORS['secondary'],
        fields=fields
    )
    
    await ctx.send(embed=embed)

@bot.command(name='refresh_support')
@is_admin()
async def refresh_support_channels(ctx):
    """Refresh support channel messages with updated buttons (ADMIN ONLY)"""
    embed = create_embed(
        "🔄 Refreshing Support Channels",
        "Clearing old messages and updating support channels...",
        color=COLORS['info']
    )
    await ctx.send(embed=embed)
    
    guild = ctx.guild
    updated_channels = []
    
    # Find and update English support channel
    en_support_channel = discord.utils.get(guild.text_channels, name=CHANNELS['en_support'])
    if en_support_channel:
        # Delete ALL messages from bot (no limit)
        deleted_count = 0
        async for message in en_support_channel.history(limit=None):
            if message.author == bot.user:
                try:
                    await message.delete()
                    deleted_count += 1
                    await asyncio.sleep(0.1)  # Rate limit protection
                except:
                    pass
        
        # Wait a moment to ensure all deletions are processed
        await asyncio.sleep(1)
        
        # Send new support message
        await setup_support_channel(en_support_channel, 'english')
        updated_channels.append(f'English ({deleted_count} old messages cleared)')
    
    # Find and update Russian support channel
    ru_support_channel = discord.utils.get(guild.text_channels, name=CHANNELS['ru_support'])
    if ru_support_channel:
        # Delete ALL messages from bot (no limit)
        deleted_count = 0
        async for message in ru_support_channel.history(limit=None):
            if message.author == bot.user:
                try:
                    await message.delete()
                    deleted_count += 1
                    await asyncio.sleep(0.1)  # Rate limit protection
                except:
                    pass
        
        # Wait a moment to ensure all deletions are processed
        await asyncio.sleep(1)
        
        # Send new support message
        await setup_support_channel(ru_support_channel, 'russian')
        updated_channels.append(f'Russian ({deleted_count} old messages cleared)')
    
    if updated_channels:
        embed = create_embed(
            "✅ Support Channels Refreshed",
            f"Updated support channels:\n• {chr(10).join(updated_channels)}\n\n"
            "Each channel now has exactly one message with the correct language button!",
            color=COLORS['success']
        )
    else:
        embed = create_embed(
            "❌ No Support Channels Found",
            "Could not find support channels. Run `!setup` first.",
            color=COLORS['error']
        )
    
    await ctx.send(embed=embed)

@bot.command(name='reset_tickets')
@is_admin()
async def reset_ticket_system(ctx):
    """Reset ticket system and clear active tickets (ADMIN ONLY)"""
    embed = create_embed(
        "🔄 Resetting Ticket System",
        "Clearing all active ticket tracking...",
        color=COLORS['info']
    )
    await ctx.send(embed=embed)
    
    # Clear active tickets from both views
    cleared_count = 0
    if english_ticket_view:
        cleared_count += len(english_ticket_view.active_tickets)
        english_ticket_view.active_tickets.clear()
    if russian_ticket_view:
        cleared_count += len(russian_ticket_view.active_tickets)
        russian_ticket_view.active_tickets.clear()
    
    embed = create_embed(
        "✅ Ticket System Reset",
        f"Cleared {cleared_count} stuck active tickets.\n"
        "Users can now create new tickets normally.",
        color=COLORS['success']
    )
    await ctx.send(embed=embed)

@bot.command(name='clear_support')
@is_admin()
async def clear_support_channels(ctx):
    """Clear all messages from support channels (ADMIN ONLY)"""
    embed = create_embed(
        "🧹 Clearing Support Channels",
        "Removing all bot messages from support channels...",
        color=COLORS['info']
    )
    await ctx.send(embed=embed)
    
    guild = ctx.guild
    cleared_channels = []
    
    # Clear English support channel
    en_support_channel = discord.utils.get(guild.text_channels, name=CHANNELS['en_support'])
    if en_support_channel:
        deleted_count = 0
        async for message in en_support_channel.history(limit=None):
            if message.author == bot.user:
                try:
                    await message.delete()
                    deleted_count += 1
                    await asyncio.sleep(0.1)
                except:
                    pass
        cleared_channels.append(f'English ({deleted_count} messages)')
    
    # Clear Russian support channel
    ru_support_channel = discord.utils.get(guild.text_channels, name=CHANNELS['ru_support'])
    if ru_support_channel:
        deleted_count = 0
        async for message in ru_support_channel.history(limit=None):
            if message.author == bot.user:
                try:
                    await message.delete()
                    deleted_count += 1
                    await asyncio.sleep(0.1)
                except:
                    pass
        cleared_channels.append(f'Russian ({deleted_count} messages)')
    
    if cleared_channels:
        embed = create_embed(
            "✅ Support Channels Cleared",
            f"Cleared channels:\n• {chr(10).join(cleared_channels)}\n\n"
            "Use `!refresh_support` to add new messages.",
            color=COLORS['success']
        )
    else:
        embed = create_embed(
            "❌ No Support Channels Found",
            "Could not find support channels to clear.",
            color=COLORS['error']
        )
    
    await ctx.send(embed=embed)

@bot.command(name='fix_bot_permissions')
@is_admin()
async def fix_bot_permissions(ctx):
    """Check and fix bot permissions (ADMIN ONLY)"""
    embed = create_embed(
        "🔧 Checking Bot Permissions",
        "Analyzing bot permissions and role assignment...",
        color=COLORS['info']
    )
    await ctx.send(embed=embed)
    
    guild = ctx.guild
    bot_member = guild.me
    
    # Find bot role
    bot_role = discord.utils.get(guild.roles, name=ROLES['bot'])
    
    issues = []
    fixes = []
    
    # Check if bot has the bot role
    if not bot_role:
        issues.append("❌ Bot role not found")
        # Try to create it
        try:
            bot_role = await safe_create_role(
                guild,
                ROLES['bot'],
                permissions=get_bot_permissions(),
                color=discord.Color.blue(),
                hoist=True,
                reason="Creating missing bot role"
            )
            if bot_role:
                fixes.append("✅ Created bot role")
            else:
                issues.append("❌ Failed to create bot role")
        except Exception as e:
            issues.append(f"❌ Error creating bot role: {e}")
    
    if bot_role and bot_role not in bot_member.roles:
        issues.append("❌ Bot missing bot role")
        try:
            await bot_member.add_roles(bot_role)
            fixes.append("✅ Added bot role to bot")
        except Exception as e:
            issues.append(f"❌ Failed to add bot role: {e}")
    
    # Check permissions in support channels
    en_support = discord.utils.get(guild.text_channels, name=CHANNELS['en_support'])
    ru_support = discord.utils.get(guild.text_channels, name=CHANNELS['ru_support'])
    
    for channel in [en_support, ru_support]:
        if channel:
            perms = channel.permissions_for(bot_member)
            channel_issues = []
            
            if not perms.create_private_threads:
                channel_issues.append("create_private_threads")
            if not perms.manage_threads:
                channel_issues.append("manage_threads")
            if not perms.send_messages:
                channel_issues.append("send_messages")
            if not perms.read_messages:
                channel_issues.append("read_messages")
            
            if channel_issues:
                issues.append(f"❌ {channel.name}: missing {', '.join(channel_issues)}")
                
                # Try to fix by setting bot role permissions
                if bot_role:
                    try:
                        await channel.set_permissions(
                            bot_role,
                            read_messages=True,
                            send_messages=True,
                            manage_messages=True,
                            manage_threads=True,
                            create_private_threads=True,
                            create_public_threads=True
                        )
                        fixes.append(f"✅ Fixed permissions in {channel.name}")
                    except Exception as e:
                        issues.append(f"❌ Failed to fix {channel.name}: {e}")
            else:
                fixes.append(f"✅ {channel.name}: permissions OK")
    
    # Create result embed
    result_parts = []
    
    if issues:
        result_parts.append("**Issues Found:**\n" + "\n".join(issues))
    
    if fixes:
        result_parts.append("**Actions Taken:**\n" + "\n".join(fixes))
    
    if not issues:
        result_parts.append("**All permissions are correctly configured! ✅**")
    
    embed = create_embed(
        "🔧 Bot Permission Check Complete",
        "\n\n".join(result_parts),
        color=COLORS['success'] if not issues else COLORS['warning']
    )
    
    await ctx.send(embed=embed)

@bot.command(name='check_tickets')
@is_admin()
async def check_active_tickets(ctx):
    """Check and display active tickets (ADMIN ONLY)"""
    embed = create_embed(
        "🎫 Checking Active Tickets",
        "Analyzing active ticket status...",
        color=COLORS['info']
    )
    await ctx.send(embed=embed)
    
    tickets_info = []
    
    # Check English tickets
    if english_ticket_view:
        english_count = len(english_ticket_view.active_tickets)
        if english_count > 0:
            tickets_info.append(f"**English Support:** {english_count} active tickets")
            # Show user IDs
            user_list = []
            for user_id in list(english_ticket_view.active_tickets):
                user = ctx.guild.get_member(user_id)
                if user:
                    user_list.append(f"• {user.name} ({user_id})")
                else:
                    user_list.append(f"• Unknown User ({user_id})")
            if user_list:
                tickets_info.append("\n".join(user_list))
        else:
            tickets_info.append("**English Support:** No active tickets")
    else:
        tickets_info.append("**English Support:** View not found")
    
    # Check Russian tickets
    if russian_ticket_view:
        russian_count = len(russian_ticket_view.active_tickets)
        if russian_count > 0:
            tickets_info.append(f"**Russian Support:** {russian_count} active tickets")
            # Show user IDs
            user_list = []
            for user_id in list(russian_ticket_view.active_tickets):
                user = ctx.guild.get_member(user_id)
                if user:
                    user_list.append(f"• {user.name} ({user_id})")
                else:
                    user_list.append(f"• Unknown User ({user_id})")
            if user_list:
                tickets_info.append("\n".join(user_list))
        else:
            tickets_info.append("**Russian Support:** No active tickets")
    else:
        tickets_info.append("**Russian Support:** View not found")
    
    embed = create_embed(
        "🎫 Active Tickets Status",
        "\n\n".join(tickets_info) if tickets_info else "No ticket information available",
        color=COLORS['info']
    )
    
    await ctx.send(embed=embed)

@bot.command(name='clear_user_tickets')
@is_admin()
async def clear_user_tickets(ctx, user_id: int):
    """Clear tickets for a specific user (ADMIN ONLY)"""
    user = ctx.guild.get_member(user_id)
    user_name = user.name if user else f"Unknown ({user_id})"
    
    cleared_count = 0
    
    # Clear from English tickets
    if english_ticket_view and user_id in english_ticket_view.active_tickets:
        english_ticket_view.remove_active_ticket(user_id)
        cleared_count += 1
    
    # Clear from Russian tickets
    if russian_ticket_view and user_id in russian_ticket_view.active_tickets:
        russian_ticket_view.remove_active_ticket(user_id)
        cleared_count += 1
    
    embed = create_embed(
        "🧹 User Tickets Cleared",
        f"Cleared {cleared_count} active tickets for {user_name}.\n"
        f"User can now create new tickets.",
        color=COLORS['success']
    )
    
    await ctx.send(embed=embed)

# SETUP FUNCTIONS

async def perform_fresh_setup(guild):
    """Perform complete server wipe and recreation"""
    logger.info(f"Starting fresh setup for {guild.name}")
    
    # Delete all channels
    for channel in guild.channels:
        await safe_delete_channel(channel)
    
    # Delete all roles except protected ones
    protected_roles = ['@everyone', guild.name, 'CSMarketCap']
    for role in guild.roles:
        if role.name not in protected_roles:
            await safe_delete_role(role)
    
    # Now perform standard setup
    await perform_server_setup(guild)

async def perform_cleanup(guild):
    """Clean server channels and roles"""
    logger.info(f"Starting cleanup for {guild.name}")
    
    # Delete channels that match our naming convention
    channels_to_delete = []
    for channel in guild.channels:
        if any(channel.name.startswith(prefix) for prefix in ['📊', '🌐', '👋', '💬', '💼', '🛠️']) or \
           any(channel.name in name for name in CHANNELS.values()):
            channels_to_delete.append(channel)
    
    for channel in channels_to_delete:
        await safe_delete_channel(channel)
    
    # Delete roles we create
    roles_to_delete = []
    for role in guild.roles:
        if role.name in ROLES.values() and role.name != '@everyone':
            roles_to_delete.append(role)
    
    for role in roles_to_delete:
        await safe_delete_role(role)

async def perform_server_setup(guild):
    """Perform complete server setup"""
    logger.info(f"Starting server setup for {guild.name}")
    
    # Step 1: Create roles
    logger.info("Creating roles...")
    guild_roles = await create_server_roles(guild)
    
    # Step 2: Create categories and channels
    logger.info("Creating server structure...")
    await create_server_structure(guild, guild_roles)
    
    logger.info("Server setup completed!")

async def create_server_roles(guild):
    """Create all server roles with proper permissions"""
    guild_roles = {'everyone': guild.default_role}
    
    # Admin role
    admin_role = await safe_create_role(
        guild, 
        ROLES['admin'],
        permissions=get_admin_permissions(),
        color=discord.Color.red(),
        hoist=True,
        reason="CSMarketCap admin role"
    )
    if admin_role:
        guild_roles['admin'] = admin_role
    
    # Moderator role
    moderator_role = await safe_create_role(
        guild,
        ROLES['moderator'],
        permissions=get_moderator_permissions(),
        color=discord.Color.orange(),
        hoist=True,
        reason="CSMarketCap moderator role"
    )
    if moderator_role:
        guild_roles['moderator'] = moderator_role
    
    # Bot role
    bot_role = await safe_create_role(
        guild,
        ROLES['bot'],
        permissions=get_bot_permissions(),
        color=discord.Color.blue(),
        hoist=True,
        reason="CSMarketCap bot role"
    )
    if bot_role:
        guild_roles['bot'] = bot_role
    
    # Member role (very restrictive)
    member_role = await safe_create_role(
        guild,
        ROLES['member'],
        permissions=get_basic_permissions(),
        color=discord.Color.green(),
        hoist=False,
        reason="CSMarketCap member role"
    )
    if member_role:
        guild_roles['member'] = member_role
    
    # Language roles (minimal permissions)
    english_role = await safe_create_role(
        guild,
        ROLES['english'],
        permissions=discord.Permissions(read_messages=True, add_reactions=True),
        color=discord.Color.from_rgb(0, 123, 255),
        hoist=False,
        reason="English language role"
    )
    if english_role:
        guild_roles['english'] = english_role
    
    russian_role = await safe_create_role(
        guild,
        ROLES['russian'],
        permissions=discord.Permissions(read_messages=True, add_reactions=True),
        color=discord.Color.from_rgb(255, 193, 7),
        hoist=False,
        reason="Russian language role"
    )
    if russian_role:
        guild_roles['russian'] = russian_role
    
    return guild_roles

async def create_server_structure(guild, guild_roles):
    """Create complete server channel structure"""
    
    # Server Stats Category
    stats_category = await safe_create_category(guild, CATEGORIES['server_stats'])
    if stats_category:
        await setup_channel_permissions(stats_category, guild_roles)
        
        # Stats voice channels
        total_members, online_members = get_member_count_stats(guild)
        await safe_create_channel(
            guild,
            CHANNELS['total_members'].format(total_members),
            category=stats_category,
            channel_type=discord.ChannelType.voice
        )
        await safe_create_channel(
            guild,
            CHANNELS['online_members'].format(online_members),
            category=stats_category,
            channel_type=discord.ChannelType.voice
        )
    
    # Language Selection Category
    language_category = await safe_create_category(guild, CATEGORIES['language_selection'])
    if language_category:
        await setup_channel_permissions(language_category, guild_roles)
        
        # Allow everyone to see language selection
        await language_category.set_permissions(guild_roles['everyone'], read_messages=True)
        
        language_channel = await safe_create_channel(
            guild,
            CHANNELS['choose_language'],
            category=language_category
        )
        if language_channel:
            await language_channel.set_permissions(guild_roles['everyone'], read_messages=True, send_messages=False)
            await setup_language_selection_channel(language_channel)
    
    # English Categories
    await create_language_channels(guild, guild_roles, 'english')
    
    # Russian Categories  
    await create_language_channels(guild, guild_roles, 'russian')

async def create_language_channels(guild, guild_roles, language):
    """Create channels for a specific language"""
    if language == 'english':
        categories_config = {
            'welcome': ('en_welcome', ['en_announcements', 'en_status', 'en_read_me']),
            'community': ('en_community', ['en_general', 'en_cs2_talk', 'en_skin_chat', 'en_price_discussion', 'en_skin_news']),
            'trading': ('en_trading', ['en_market', 'en_looking_for', 'en_price_check']),
            'support': ('en_support', ['en_support'])
        }
        language_role = guild_roles['english']
    else:
        categories_config = {
            'welcome': ('ru_welcome', ['ru_announcements', 'ru_status', 'ru_read_me']),
            'community': ('ru_community', ['ru_general', 'ru_cs2_talk', 'ru_skin_chat', 'ru_price_discussion', 'ru_skin_news']),
            'trading': ('ru_trading', ['ru_market', 'ru_looking_for', 'ru_price_check']),
            'support': ('ru_support', ['ru_support'])
        }
        language_role = guild_roles['russian']
    
    for category_type, (category_key, channel_keys) in categories_config.items():
        category = await safe_create_category(guild, CATEGORIES[category_key])
        if not category:
            continue
            
        # Set basic permissions
        await setup_channel_permissions(category, guild_roles)
        
        for channel_key in channel_keys:
            channel = await safe_create_channel(guild, CHANNELS[channel_key], category=category)
            if not channel:
                continue
            
            # Apply specific permissions based on category type
            if category_type == 'welcome':
                await setup_welcome_channel_permissions(channel, guild_roles, language_role)
                await send_welcome_channel_content(channel, language)
            elif category_type == 'community' or category_type == 'trading':
                await setup_community_channel_permissions(channel, guild_roles, language_role)
                await send_channel_content(channel, channel_key, language)
            elif category_type == 'support':
                await setup_support_channel_permissions(channel, guild_roles, language_role)
                await setup_support_channel(channel, language)

async def setup_language_selection_channel(channel):
    """Setup language selection channel with embed and buttons"""
    embed = create_embed(
        "🌐 Language Selection",
        "**Welcome to CSMarketCap!**\n"
        "Choose your preferred language to access the appropriate channels.\n\n"
        "🇺🇸 **English** - Access English channels\n"
        "🇷🇺 **Русский** - Доступ к русским каналам\n\n"
        "**После выбора языка вы получите:**\n"
        "• Доступ к каналам на выбранном языке\n"
        "• Руководство по каналам в ЛС\n"
        "• Возможность торговать и общаться\n\n"
        "**After selecting a language you will get:**\n"
        "• Access to channels in your chosen language\n"
        "• Channel guide via DM\n"
        "• Ability to trade and communicate",
        color=COLORS['primary']
    )
    
    await channel.send(embed=embed, view=language_view)

async def setup_support_channel(channel, language):
    """Setup support channel with ticket creation button"""
    if language == 'english':
        embed = create_embed(
            "🆘 Support Center",
            "**Need help?** Our support team is here to assist you!\n\n"
            "**How to get support:**\n"
            "• Click the button below to create a private ticket\n"
            "• Describe your issue in detail\n"
            "• Our staff will respond as soon as possible\n\n"
            "**What we help with:**\n"
            "🔹 Trading disputes and scam reports\n"
            "🔹 Technical issues with the server\n"
            "🔹 Account problems and verification\n"
            "🔹 General questions about CS2 trading\n"
            "🔹 Channel access and permission issues\n\n"
            "**Response time:** Usually within 24 hours\n"
            "**Language:** English support",
            color=COLORS['info']
        )
        # Create a simple view with only the English button visible
        view = SimpleTicketView('english')
    else:
        embed = create_embed(
            "🆘 Центр поддержки",
            "**Нужна помощь?** Наша команда поддержки готова вам помочь!\n\n"
            "**Как получить поддержку:**\n"
            "• Нажмите кнопку ниже, чтобы создать приватный тикет\n"
            "• Подробно опишите вашу проблему\n"
            "• Наш персонал ответит как можно скорее\n\n"
            "**С чем мы помогаем:**\n"
            "🔹 Торговые споры и жалобы на мошенников\n"
            "🔹 Технические проблемы с сервером\n"
            "🔹 Проблемы с аккаунтом и верификацией\n"
            "🔹 Общие вопросы о торговле CS2\n"
            "🔹 Доступ к каналам и проблемы с правами\n\n"
            "**Время ответа:** Обычно в течение 24 часов\n"
            "**Язык:** Поддержка на русском языке",
            color=COLORS['info']
        )
        # Create a simple view with only the Russian button visible
        view = SimpleTicketView('russian')
    
    await channel.send(embed=embed, view=view)

async def send_welcome_channel_content(channel, language):
    """Send welcome content to welcome category channels"""
    if 'announcements' in channel.name or 'объявления' in channel.name:
        if language == 'english':
            embed = create_embed(
                "📢 Welcome to CSMarketCap Announcements",
                "**This channel is for important server announcements only.**\n\n"
                "Here you'll find:\n"
                "🔹 Server updates and changes\n"
                "🔹 New features and improvements\n"
                "🔹 Community events and tournaments\n"
                "🔹 Important policy changes\n"
                "🔹 Maintenance notifications\n\n"
                "*This is a read-only channel for regular members.*",
                color=COLORS['primary']
            )
        else:
            embed = create_embed(
                "📢 Добро пожаловать в объявления CSMarketCap",
                "**Этот канал только для важных объявлений сервера.**\n\n"
                "Здесь вы найдете:\n"
                "🔹 Обновления и изменения сервера\n"
                "🔹 Новые функции и улучшения\n"
                "🔹 События сообщества и турниры\n"
                "🔹 Важные изменения политики\n"
                "🔹 Уведомления о техническом обслуживании\n\n"
                "*Это канал только для чтения для обычных участников.*",
                color=COLORS['primary']
            )
        await channel.send(embed=embed)

async def send_channel_content(channel, channel_key, language):
    """Send appropriate content to specific channels"""
    # This would contain detailed channel descriptions and pinned messages
    # For brevity, I'll just add a basic welcome message
    if language == 'english':
        if 'general' in channel.name:
            embed = create_embed(
                "💬 General Chat",
                "Welcome to the general discussion channel!\n\n"
                "**Channel Rules:**\n"
                "• Keep discussions friendly and respectful\n"
                "• No spam or excessive caps\n"
                "• Use appropriate channels for specific topics\n"
                "• Have fun and be part of the community!\n\n"
                "Let's chat about CS2, trading, and community topics! 🎮",
                color=COLORS['secondary']
            )
        elif 'market' in channel.name:
            embed = create_embed(
                "💸 Trading Market",
                "Welcome to the CS2 trading market!\n\n"
                "**Trading Guidelines:**\n"
                "• Always use Steam trade offers\n"
                "• Check prices before trading\n"
                "• Beware of scammers\n"
                "• Use middleman services for high-value trades\n"
                "• Report suspicious activity\n\n"
                "Happy trading! 📈",
                color=COLORS['success']
            )
        else:
            embed = create_embed(
                f"Welcome to {channel.name}",
                "This channel is part of the CSMarketCap community.\n"
                "Please follow server rules and enjoy your stay!",
                color=COLORS['info']
            )
    else:
        if 'общий' in channel.name:
            embed = create_embed(
                "💬 Общий чат",
                "Добро пожаловать в канал общих обсуждений!\n\n"
                "**Правила канала:**\n"
                "• Ведите дружелюбные и уважительные обсуждения\n"
                "• Без спама и чрезмерного использования капса\n"
                "• Используйте соответствующие каналы для конкретных тем\n"
                "• Веселитесь и будьте частью сообщества!\n\n"
                "Давайте общаться о CS2, торговле и темах сообщества! 🎮",
                color=COLORS['secondary']
            )
        elif 'рынок' in channel.name:
            embed = create_embed(
                "💸 Торговый рынок",
                "Добро пожаловать на торговый рынок CS2!\n\n"
                "**Правила торговли:**\n"
                "• Всегда используйте торговые предложения Steam\n"
                "• Проверяйте цены перед торговлей\n"
                "• Остерегайтесь мошенников\n"
                "• Используйте услуги посредника для дорогих сделок\n"
                "• Сообщайте о подозрительной активности\n\n"
                "Удачной торговли! 📈",
                color=COLORS['success']
            )
        else:
            embed = create_embed(
                f"Добро пожаловать в {channel.name}",
                "Этот канал является частью сообщества CSMarketCap.\n"
                "Пожалуйста, соблюдайте правила сервера и приятного пребывания!",
                color=COLORS['info']
            )
    
    await channel.send(embed=embed)

# Run the bot
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        logger.error("Please create a .env file with your bot token.")
        exit(1)
    
    try:
        bot.run(DISCORD_TOKEN)
    except discord.LoginFailure:
        logger.error("Invalid bot token! Please check your DISCORD_TOKEN in .env file.")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        traceback.print_exc() 