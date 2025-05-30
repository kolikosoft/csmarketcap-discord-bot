import discord
from discord.ext import commands
from datetime import datetime, timezone, timedelta
import asyncio
from utils import create_embed, logger
from config import COLORS, ROLES
import traceback

class LanguageSelectionView(discord.ui.View):
    """Persistent view for language selection with cooldown protection"""
    
    def __init__(self):
        super().__init__(timeout=None)
        self.cooldowns = {}  # Track user cooldowns
        
    def is_on_cooldown(self, user_id):
        """Check if user is on cooldown"""
        if user_id in self.cooldowns:
            time_left = self.cooldowns[user_id] - datetime.now(timezone.utc)
            if time_left.total_seconds() > 0:
                return True, time_left.total_seconds()
        return False, 0
    
    def set_cooldown(self, user_id, seconds=5):
        """Set cooldown for user"""
        self.cooldowns[user_id] = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    
    async def assign_language_role(self, interaction, language):
        """Assign language role and remove other language roles"""
        try:
            guild = interaction.guild
            user = interaction.user
            
            # Get roles
            english_role = discord.utils.get(guild.roles, name=ROLES['english'])
            russian_role = discord.utils.get(guild.roles, name=ROLES['russian'])
            
            if not english_role or not russian_role:
                embed = create_embed(
                    "❌ Error",
                    "Language roles not found. Please contact an administrator.",
                    color=COLORS['error']
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Remove existing language roles
            roles_to_remove = []
            if english_role in user.roles:
                roles_to_remove.append(english_role)
            if russian_role in user.roles:
                roles_to_remove.append(russian_role)
            
            if roles_to_remove:
                await user.remove_roles(*roles_to_remove)
            
            # Add new language role
            new_role = english_role if language == 'english' else russian_role
            await user.add_roles(new_role)
            
            # Create success embed
            if language == 'english':
                embed = create_embed(
                    "🇺🇸 English Selected",
                    "Welcome to CSMarketCap! You now have access to English channels.\n\n"
                    "**Available Channels:**\n"
                    "• **Welcome**: Announcements and information\n"
                    "• **Community**: General discussions about CS2 and skins\n"
                    "• **Trading**: Market discussions and trading\n"
                    "• **Support**: Get help from our team\n\n"
                    "Happy trading! 🎮",
                    color=COLORS['success']
                )
                dm_embed = create_embed(
                    "🇺🇸 Welcome to CSMarketCap!",
                    f"Hi {user.mention}! You've selected English as your language.\n\n"
                    "**Channel Guide:**\n"
                    "📢 **Announcements** - Important server updates\n"
                    "💬 **General** - Chat with the community\n"
                    "🎮 **CS2 Talk** - Discuss Counter-Strike 2\n"
                    "🎨 **Skin Chat** - Show off your skins\n"
                    "📉 **Price Discussion** - Market analysis\n"
                    "💸 **Market** - Trading hub\n"
                    "🔍 **Price Check** - Get price estimates\n"
                    "🆘 **Support** - Need help? Create a ticket!\n\n"
                    "Enjoy your stay! 🚀",
                    color=COLORS['info']
                )
            else:
                embed = create_embed(
                    "🇷🇺 Русский выбран",
                    "Добро пожаловать в CSMarketCap! Теперь у вас есть доступ к русским каналам.\n\n"
                    "**Доступные каналы:**\n"
                    "• **Добро пожаловать**: Объявления и информация\n"
                    "• **Сообщество**: Общие обсуждения CS2 и скинов\n"
                    "• **Торговля**: Обсуждения рынка и торговли\n"
                    "• **Поддержка**: Получите помощь от нашей команды\n\n"
                    "Удачной торговли! 🎮",
                    color=COLORS['success']
                )
                dm_embed = create_embed(
                    "🇷🇺 Добро пожаловать в CSMarketCap!",
                    f"Привет {user.mention}! Вы выбрали русский язык.\n\n"
                    "**Руководство по каналам:**\n"
                    "📢 **Объявления** - Важные обновления сервера\n"
                    "💬 **Общий** - Общайтесь с сообществом\n"
                    "🎮 **CS2 обсуждение** - Обсуждайте Counter-Strike 2\n"
                    "🎨 **Скины чат** - Покажите свои скины\n"
                    "📉 **Обсуждение цен** - Анализ рынка\n"
                    "💸 **Рынок** - Торговый центр\n"
                    "🔍 **Проверка цены** - Получите оценки цен\n"
                    "🆘 **Поддержка** - Нужна помощь? Создайте тикет!\n\n"
                    "Приятного пребывания! 🚀",
                    color=COLORS['info']
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Send DM with channel guide
            try:
                await user.send(embed=dm_embed)
            except discord.Forbidden:
                logger.warning(f"Could not send DM to {user.name} - DMs disabled")
            
            logger.info(f"User {user.name} selected {language} language")
            
        except Exception as e:
            logger.error(f"Error assigning language role: {e}")
            traceback.print_exc()
            
            embed = create_embed(
                "❌ Error",
                "An error occurred while assigning your language role. Please try again or contact an administrator.",
                color=COLORS['error']
            )
            
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label='🇺🇸 English', style=discord.ButtonStyle.primary, custom_id='language_english')
    async def english_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle English language selection"""
        user_id = interaction.user.id
        on_cooldown, time_left = self.is_on_cooldown(user_id)
        
        if on_cooldown:
            embed = create_embed(
                "⏰ Cooldown",
                f"Please wait {time_left:.1f} seconds before selecting a language again.",
                color=COLORS['warning']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        self.set_cooldown(user_id)
        await self.assign_language_role(interaction, 'english')

    @discord.ui.button(label='🇷🇺 Русский', style=discord.ButtonStyle.primary, custom_id='language_russian')
    async def russian_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle Russian language selection"""
        user_id = interaction.user.id
        on_cooldown, time_left = self.is_on_cooldown(user_id)
        
        if on_cooldown:
            embed = create_embed(
                "⏰ Кулдаун",
                f"Пожалуйста, подождите {time_left:.1f} секунд перед повторным выбором языка.",
                color=COLORS['warning']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        self.set_cooldown(user_id)
        await self.assign_language_role(interaction, 'russian')


class SimpleTicketView(discord.ui.View):
    """Simplified ticket view that works reliably"""
    
    def __init__(self, language):
        super().__init__(timeout=None)
        self.language = language
        self.cooldowns = {}
        self.active_tickets = set()
        
        # Add language-specific button
        if language == 'english':
            self.add_item(SimpleTicketButton('english'))
        else:
            self.add_item(SimpleTicketButton('russian'))
        
    def is_on_cooldown(self, user_id):
        """Check if user is on cooldown"""
        if user_id in self.cooldowns:
            time_left = self.cooldowns[user_id] - datetime.now(timezone.utc)
            if time_left.total_seconds() > 0:
                return True, time_left.total_seconds()
        return False, 0
    
    def set_cooldown(self, user_id, seconds=5):
        """Set cooldown for user"""
        self.cooldowns[user_id] = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    
    def has_active_ticket(self, user_id):
        """Check if user has an active ticket"""
        return user_id in self.active_tickets
    
    def add_active_ticket(self, user_id):
        """Add user to active tickets"""
        self.active_tickets.add(user_id)
    
    def remove_active_ticket(self, user_id):
        """Remove user from active tickets"""
        self.active_tickets.discard(user_id)


class SimpleTicketButton(discord.ui.Button):
    """Language-specific ticket button"""
    
    def __init__(self, language):
        self.language = language
        if language == 'english':
            super().__init__(
                label='🎫 Create Ticket',
                style=discord.ButtonStyle.success,
                custom_id='simple_ticket_english'
            )
        else:
            super().__init__(
                label='🎫 Создать тикет',
                style=discord.ButtonStyle.success,
                custom_id='simple_ticket_russian'
            )
    
    async def callback(self, interaction: discord.Interaction):
        """Create a support ticket"""
        # Get the view that contains this button
        view = self.view
        if not isinstance(view, SimpleTicketView):
            logger.error(f"Ticket button view is not SimpleTicketView: {type(view)}")
            return
            
        try:
            user = interaction.user
            user_id = user.id
            guild = interaction.guild
            channel = interaction.channel
            
            logger.info(f"Ticket creation attempt by {user.name} ({user_id}) in {channel.name}")
            
            # Check bot permissions first
            bot_member = guild.me
            bot_permissions = channel.permissions_for(bot_member)
            
            logger.info(f"Bot permissions in {channel.name}: "
                       f"create_private_threads={bot_permissions.create_private_threads}, "
                       f"manage_threads={bot_permissions.manage_threads}, "
                       f"send_messages={bot_permissions.send_messages}")
            
            if not bot_permissions.create_private_threads:
                logger.error(f"Bot missing create_private_threads permission in {channel.name}")
                embed = create_embed(
                    "❌ Permission Error",
                    "Bot doesn't have permission to create threads in this channel. Please contact an administrator.",
                    color=COLORS['error']
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Check cooldown
            on_cooldown, time_left = view.is_on_cooldown(user_id)
            if on_cooldown:
                logger.info(f"User {user.name} on cooldown: {time_left:.1f}s remaining")
                if self.language == 'english':
                    embed = create_embed(
                        "⏰ Cooldown",
                        f"Please wait {time_left:.1f} seconds before creating another ticket.",
                        color=COLORS['warning']
                    )
                else:
                    embed = create_embed(
                        "⏰ Кулдаун",
                        f"Пожалуйста, подождите {time_left:.1f} секунд перед созданием нового тикета.",
                        color=COLORS['warning']
                    )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Check for existing ticket
            if view.has_active_ticket(user_id):
                logger.info(f"User {user.name} already has active ticket")
                if self.language == 'english':
                    embed = create_embed(
                        "❌ Existing Ticket",
                        "You already have an active support ticket. Please use your existing ticket or close it first.",
                        color=COLORS['error']
                    )
                else:
                    embed = create_embed(
                        "❌ Существующий тикет",
                        "У вас уже есть активный тикет поддержки. Пожалуйста, используйте существующий тикет или закройте его сначала.",
                        color=COLORS['error']
                    )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Create immediate response
            logger.info(f"Creating ticket for {user.name} in {self.language}")
            if self.language == 'english':
                embed = create_embed(
                    "🔄 Creating Ticket",
                    "Creating your support ticket...",
                    color=COLORS['info']
                )
            else:
                embed = create_embed(
                    "🔄 Создание тикета",
                    "Создаем ваш тикет поддержки...",
                    color=COLORS['info']
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"Sent initial response for {user.name}")
            
            # Set cooldown and add to active
            view.set_cooldown(user_id)
            view.add_active_ticket(user_id)
            logger.info(f"Set cooldown and added {user.name} to active tickets")
            
            # Create thread
            thread_name = f"🎫 {user.display_name}"
            logger.info(f"Attempting to create thread '{thread_name}' in {channel.name}")
            
            try:
                thread = await channel.create_thread(
                    name=thread_name,
                    type=discord.ChannelType.public_thread,
                    reason=f"Support ticket created by {user.name}"
                )
                logger.info(f"Successfully created thread {thread.name} ({thread.id})")
                
                # For public threads, the creator is automatically added
                # But let's ensure they have access
                try:
                    await thread.add_user(user)
                    logger.info(f"Added ticket creator {user.name} to thread")
                except Exception as e:
                    logger.info(f"User {user.name} already has access to public thread: {e}")
                    
            except discord.Forbidden as e:
                logger.error(f"Forbidden to create thread: {e}")
                error_embed = create_embed(
                    "❌ Permission Error",
                    "Bot doesn't have permission to create threads. Please contact an administrator.",
                    color=COLORS['error']
                )
                await interaction.edit_original_response(embed=error_embed)
                view.remove_active_ticket(user_id)
                return
            except Exception as e:
                logger.error(f"Error creating thread: {e}")
                raise
            
            # Add staff to thread
            admin_role = discord.utils.get(guild.roles, name=ROLES['admin'])
            moderator_role = discord.utils.get(guild.roles, name=ROLES['moderator'])
            
            staff_added = 0
            if admin_role:
                logger.info(f"Adding {len(admin_role.members)} admins to thread")
                for member in admin_role.members:
                    try:
                        await thread.add_user(member)
                        staff_added += 1
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.warning(f"Could not add admin {member.name} to thread: {e}")
            
            if moderator_role:
                logger.info(f"Adding {len(moderator_role.members)} moderators to thread")
                for member in moderator_role.members:
                    try:
                        await thread.add_user(member)
                        staff_added += 1
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.warning(f"Could not add moderator {member.name} to thread: {e}")
            
            logger.info(f"Added {staff_added} staff members to thread")
            
            # Send welcome message in thread
            if self.language == 'english':
                ticket_embed = create_embed(
                    "🎫 Support Ticket Created",
                    f"Hello {user.mention}! Welcome to your support ticket.\n\n"
                    "Please describe your issue and our team will help you.",
                    color=COLORS['success']
                )
                success_embed = create_embed(
                    "✅ Ticket Created",
                    f"Your ticket has been created: {thread.mention}",
                    color=COLORS['success']
                )
            else:
                ticket_embed = create_embed(
                    "🎫 Тикет поддержки создан",
                    f"Привет {user.mention}! Добро пожаловать в ваш тикет поддержки.\n\n"
                    "Пожалуйста, опишите вашу проблему и наша команда поможет вам.",
                    color=COLORS['success']
                )
                success_embed = create_embed(
                    "✅ Тикет создан",
                    f"Ваш тикет был создан: {thread.mention}",
                    color=COLORS['success']
                )
            
            # Send messages
            close_view = TicketCloseView(user_id, self.language)
            logger.info(f"Sending welcome message to thread")
            await thread.send(embed=ticket_embed, view=close_view)
            logger.info(f"Editing original response with success message")
            await interaction.edit_original_response(embed=success_embed)
            
            logger.info(f"Successfully completed ticket creation for {user.name}")
            
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            traceback.print_exc()
            
            # Remove from active tickets on error
            if 'view' in locals() and 'user_id' in locals():
                view.remove_active_ticket(user_id)
            
            try:
                if self.language == 'english':
                    error_embed = create_embed("❌ Error", f"Failed to create ticket: {str(e)}", color=COLORS['error'])
                else:
                    error_embed = create_embed("❌ Ошибка", f"Не удалось создать тикет: {str(e)}", color=COLORS['error'])
                
                if not interaction.response.is_done():
                    await interaction.response.send_message(embed=error_embed, ephemeral=True)
                else:
                    await interaction.edit_original_response(embed=error_embed)
            except Exception as edit_error:
                logger.error(f"Failed to send error message: {edit_error}")


class TicketCloseView(discord.ui.View):
    """View for closing support tickets"""
    
    def __init__(self, ticket_owner_id, language='english'):
        super().__init__(timeout=None)
        self.ticket_owner_id = ticket_owner_id
        self.language = language
        
        # Add the appropriate close button based on language
        if language == 'english':
            self.add_item(CloseTicketButton('english'))
        else:
            self.add_item(CloseTicketButton('russian'))
    
    async def close_ticket(self, interaction):
        """Close the support ticket"""
        try:
            user = interaction.user
            guild = interaction.guild
            
            # Check permissions - only ticket owner, admins, or moderators can close
            admin_role = discord.utils.get(guild.roles, name=ROLES['admin'])
            moderator_role = discord.utils.get(guild.roles, name=ROLES['moderator'])
            
            can_close = (
                user.id == self.ticket_owner_id or
                (admin_role and admin_role in user.roles) or
                (moderator_role and moderator_role in user.roles)
            )
            
            if not can_close:
                embed = create_embed(
                    "❌ No Permission" if self.language == 'english' else "❌ Нет разрешения",
                    "Only the ticket owner or staff can close this ticket." if self.language == 'english'
                    else "Только владелец тикета или персонал могут закрыть этот тикет.",
                    color=COLORS['error']
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Create closing embed
            if self.language == 'english':
                embed = create_embed(
                    "🔒 Ticket Closing",
                    f"This ticket is being closed by {user.mention}.\n"
                    "The thread will be archived in 5 seconds.\n\n"
                    "Thank you for using CSMarketCap support!",
                    color=COLORS['info']
                )
            else:
                embed = create_embed(
                    "🔒 Закрытие тикета",
                    f"Этот тикет закрывается пользователем {user.mention}.\n"
                    "Тред будет заархивирован через 5 секунд.\n\n"
                    "Спасибо за использование поддержки CSMarketCap!",
                    color=COLORS['info']
                )
            
            await interaction.response.send_message(embed=embed)
            
            # Remove from active tickets in all views - CRITICAL FIX
            logger.info(f"Removing user {self.ticket_owner_id} from all active ticket lists")
            
            # Remove from the current thread's view if we can find it
            # First try to find the view that created this ticket
            channel = interaction.channel
            if hasattr(channel, 'parent') and channel.parent:
                # This is a thread, get the parent channel
                parent_channel = channel.parent
                
                # Try to find the message with the ticket view in the parent channel
                try:
                    async for message in parent_channel.history(limit=50):
                        if message.author.bot and message.components:
                            for component in message.components:
                                if hasattr(component, 'children'):
                                    for child in component.children:
                                        if hasattr(child, 'custom_id') and 'ticket' in str(child.custom_id):
                                            # This message has a ticket button, get its view
                                            view = discord.ui.View.from_message(message)
                                            if hasattr(view, 'remove_active_ticket'):
                                                view.remove_active_ticket(self.ticket_owner_id)
                                                logger.info(f"Removed from ticket view in {parent_channel.name}")
                                            break
                except Exception as e:
                    logger.warning(f"Could not clean up view in parent channel: {e}")
            
            # Also try to access global ticket views
            try:
                from bot import english_ticket_view, russian_ticket_view
                removed_count = 0
                if english_ticket_view and hasattr(english_ticket_view, 'remove_active_ticket'):
                    if self.ticket_owner_id in english_ticket_view.active_tickets:
                        english_ticket_view.remove_active_ticket(self.ticket_owner_id)
                        removed_count += 1
                        logger.info("Removed from english_ticket_view")
                if russian_ticket_view and hasattr(russian_ticket_view, 'remove_active_ticket'):
                    if self.ticket_owner_id in russian_ticket_view.active_tickets:
                        russian_ticket_view.remove_active_ticket(self.ticket_owner_id)
                        removed_count += 1
                        logger.info("Removed from russian_ticket_view")
                
                logger.info(f"Removed user from {removed_count} global ticket views")
            except ImportError:
                logger.warning("Could not access global ticket views for cleanup")
            except Exception as e:
                logger.warning(f"Error cleaning up global ticket views: {e}")
            
            # Wait and then archive
            await asyncio.sleep(5)
            
            thread = interaction.channel
            if isinstance(thread, discord.Thread):
                await thread.edit(archived=True, reason=f"Ticket closed by {user.name}")
                logger.info(f"Ticket closed by {user.name}")
            
        except Exception as e:
            logger.error(f"Error closing ticket: {e}")
            traceback.print_exc()


class CloseTicketButton(discord.ui.Button):
    """Individual button for closing tickets"""
    
    def __init__(self, language):
        self.language = language
        if language == 'english':
            super().__init__(
                label='🔒 Close Ticket',
                style=discord.ButtonStyle.danger,
                custom_id='close_ticket_en'
            )
        else:
            super().__init__(
                label='🔒 Закрыть тикет',
                style=discord.ButtonStyle.danger,
                custom_id='close_ticket_ru'
            )
    
    async def callback(self, interaction: discord.Interaction):
        # Get the view instance
        view = self.view
        if isinstance(view, TicketCloseView):
            await view.close_ticket(interaction)


# Legacy class for backwards compatibility
class TicketView(discord.ui.View):
    """Legacy ticket view - redirects to unified view"""
    
    def __init__(self, language='english'):
        super().__init__(timeout=None)
        self.language = language
        self.cooldowns = {}
        self.active_tickets = set()
        
        # This is now just a wrapper - actual functionality is in UnifiedTicketView
        
    def is_on_cooldown(self, user_id):
        return False, 0
    
    def set_cooldown(self, user_id, seconds=5):
        pass
    
    def has_active_ticket(self, user_id):
        return False
    
    def add_active_ticket(self, user_id):
        pass
    
    def remove_active_ticket(self, user_id):
        pass

    async def create_ticket(self, interaction, language):
        # This should not be called anymore
        logger.warning("Legacy TicketView.create_ticket called - this should not happen")
        pass 

class LanguageSpecificTicketView(discord.ui.View):
    """View that shows only one button per language and delegates to unified view"""
    
    def __init__(self, language):
        super().__init__(timeout=None)
        self.language = language
        
        if language == 'english':
            self.add_item(SingleLanguageTicketButton('english'))
        else:
            self.add_item(SingleLanguageTicketButton('russian'))


class SingleLanguageTicketButton(discord.ui.Button):
    """Single language ticket button that delegates to unified view"""
    
    def __init__(self, language):
        self.language = language
        if language == 'english':
            super().__init__(
                label='🎫 Create Ticket',
                style=discord.ButtonStyle.success,
                custom_id=f'single_ticket_en'
            )
        else:
            super().__init__(
                label='🎫 Создать тикет',
                style=discord.ButtonStyle.success,
                custom_id=f'single_ticket_ru'
            )
    
    async def callback(self, interaction: discord.Interaction):
        # Delegate to the unified ticket view
        try:
            from bot import unified_ticket_view
            if unified_ticket_view:
                await unified_ticket_view.create_ticket(interaction, self.language)
            else:
                # Fallback - create a temporary unified view
                temp_view = UnifiedTicketView()
                await temp_view.create_ticket(interaction, self.language)
        except ImportError:
            # Fallback - create a temporary unified view
            temp_view = UnifiedTicketView()
            await temp_view.create_ticket(interaction, self.language)


# Legacy class for backwards compatibility 