import discord
from discord.ext import commands
from datetime import datetime, timezone
import asyncio
from config import ROLES, COLORS
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_admin():
    """Decorator to check if user has Admin role"""
    async def predicate(ctx):
        if not ctx.guild:
            return False
        
        admin_role = discord.utils.get(ctx.guild.roles, name=ROLES['admin'])
        if not admin_role:
            await ctx.send("❌ Admin role not found in this server.")
            return False
            
        if admin_role not in ctx.author.roles:
            await ctx.send("❌ This command is restricted to Administrators only.")
            return False
        
        return True
    
    return commands.check(predicate)

def create_embed(title, description, color=COLORS['primary'], thumbnail=None, fields=None):
    """Create a standardized embed"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now(timezone.utc)
    )
    
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    
    if fields:
        for field in fields:
            embed.add_field(
                name=field.get('name', 'Field'),
                value=field.get('value', 'No value'),
                inline=field.get('inline', False)
            )
    
    embed.set_footer(text="CSMarketCap • CS2 Trading Community")
    return embed

async def safe_delete_channel(channel):
    """Safely delete a channel with error handling"""
    try:
        if channel:
            await channel.delete()
            logger.info(f"Deleted channel: {channel.name}")
    except discord.NotFound:
        logger.warning(f"Channel {channel} not found during deletion")
    except discord.Forbidden:
        logger.error(f"No permission to delete channel {channel}")
    except Exception as e:
        logger.error(f"Error deleting channel {channel}: {e}")

async def safe_delete_role(role):
    """Safely delete a role with error handling"""
    try:
        if role and role.name not in ['@everyone', 'CSMarketCap']:
            await role.delete()
            logger.info(f"Deleted role: {role.name}")
    except discord.NotFound:
        logger.warning(f"Role {role} not found during deletion")
    except discord.Forbidden:
        logger.error(f"No permission to delete role {role}")
    except Exception as e:
        logger.error(f"Error deleting role {role}: {e}")

async def safe_create_role(guild, name, **kwargs):
    """Safely create a role with error handling"""
    try:
        role = await guild.create_role(name=name, **kwargs)
        logger.info(f"Created role: {name}")
        return role
    except discord.Forbidden:
        logger.error(f"No permission to create role {name}")
        return None
    except Exception as e:
        logger.error(f"Error creating role {name}: {e}")
        return None

async def safe_create_category(guild, name, **kwargs):
    """Safely create a category with error handling"""
    try:
        category = await guild.create_category(name, **kwargs)
        logger.info(f"Created category: {name}")
        await asyncio.sleep(0.5)  # Rate limit protection
        return category
    except discord.Forbidden:
        logger.error(f"No permission to create category {name}")
        return None
    except Exception as e:
        logger.error(f"Error creating category {name}: {e}")
        return None

async def safe_create_channel(guild, name, category=None, channel_type=discord.ChannelType.text, **kwargs):
    """Safely create a channel with error handling"""
    try:
        if channel_type == discord.ChannelType.voice:
            channel = await guild.create_voice_channel(name, category=category, **kwargs)
        else:
            channel = await guild.create_text_channel(name, category=category, **kwargs)
        
        logger.info(f"Created {channel_type.name} channel: {name}")
        await asyncio.sleep(0.5)  # Rate limit protection
        return channel
    except discord.Forbidden:
        logger.error(f"No permission to create channel {name}")
        return None
    except Exception as e:
        logger.error(f"Error creating channel {name}: {e}")
        return None

def get_basic_permissions():
    """Get basic member permissions (very restrictive)"""
    return discord.Permissions(
        read_messages=True,
        send_messages=False,  # Will be overridden per channel
        add_reactions=True,
        read_message_history=True,
        use_external_emojis=False,
        embed_links=False,
        attach_files=False,
        mention_everyone=False,
        manage_messages=False,
        manage_channels=False,
        kick_members=False,
        ban_members=False,
        administrator=False,
        connect=False,
        speak=False,
        stream=False,
        use_voice_activation=False
    )

def get_moderator_permissions():
    """Get moderator permissions"""
    return discord.Permissions(
        read_messages=True,
        send_messages=True,
        manage_messages=True,
        manage_channels=True,
        kick_members=True,
        ban_members=True,
        add_reactions=True,
        read_message_history=True,
        use_external_emojis=True,
        embed_links=True,
        attach_files=True,
        mention_everyone=True,
        manage_threads=True,
        connect=True,
        speak=True,
        mute_members=True,
        deafen_members=True,
        move_members=True
    )

def get_admin_permissions():
    """Get admin permissions"""
    return discord.Permissions.all()

def get_bot_permissions():
    """Get bot permissions"""
    return discord.Permissions(
        read_messages=True,
        send_messages=True,
        manage_messages=True,
        manage_channels=True,
        manage_roles=True,
        add_reactions=True,
        read_message_history=True,
        use_external_emojis=True,
        embed_links=True,
        attach_files=True,
        mention_everyone=True,
        manage_threads=True,
        create_public_threads=True,
        create_private_threads=True,
        connect=True,
        speak=True
    )

async def setup_channel_permissions(channel, guild_roles):
    """Setup permissions for a channel based on its type"""
    try:
        # Default: deny access to @everyone
        await channel.set_permissions(guild_roles['everyone'], read_messages=False)
        
        # Admin and Bot: full access
        await channel.set_permissions(guild_roles['admin'], read_messages=True, send_messages=True, manage_messages=True)
        await channel.set_permissions(guild_roles['bot'], read_messages=True, send_messages=True, manage_messages=True)
        
        # Moderator: manage access but can't use bot commands
        await channel.set_permissions(guild_roles['moderator'], read_messages=True, send_messages=True, manage_messages=True)
        
        logger.info(f"Set up basic permissions for channel: {channel.name}")
        
    except Exception as e:
        logger.error(f"Error setting up permissions for {channel.name}: {e}")

async def setup_welcome_channel_permissions(channel, guild_roles, language_role):
    """Setup read-only permissions for welcome category channels"""
    try:
        await setup_channel_permissions(channel, guild_roles)
        
        # Language role: read-only access
        await channel.set_permissions(
            language_role, 
            read_messages=True, 
            send_messages=False, 
            add_reactions=True,
            read_message_history=True
        )
        
        logger.info(f"Set up welcome permissions for channel: {channel.name}")
        
    except Exception as e:
        logger.error(f"Error setting up welcome permissions for {channel.name}: {e}")

async def setup_community_channel_permissions(channel, guild_roles, language_role):
    """Setup read-write permissions for community category channels"""
    try:
        await setup_channel_permissions(channel, guild_roles)
        
        # Language role: read-write access
        await channel.set_permissions(
            language_role, 
            read_messages=True, 
            send_messages=True, 
            add_reactions=True,
            read_message_history=True,
            embed_links=False,  # Restrictive
            attach_files=False  # Restrictive
        )
        
        logger.info(f"Set up community permissions for channel: {channel.name}")
        
    except Exception as e:
        logger.error(f"Error setting up community permissions for {channel.name}: {e}")

async def setup_support_channel_permissions(channel, guild_roles, language_role):
    """Setup read-only permissions for support channels (buttons only)"""
    try:
        await setup_channel_permissions(channel, guild_roles)
        
        # Language role: read-only but can interact with buttons
        await channel.set_permissions(
            language_role, 
            read_messages=True, 
            send_messages=False, 
            add_reactions=True,
            read_message_history=True
        )
        
        logger.info(f"Set up support permissions for channel: {channel.name}")
        
    except Exception as e:
        logger.error(f"Error setting up support permissions for {channel.name}: {e}")

def get_member_count_stats(guild):
    """Get member count statistics"""
    total_members = guild.member_count
    online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
    
    return total_members, online_members 