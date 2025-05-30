import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Discord Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID')) if os.getenv('GUILD_ID') else None

# Bot Settings
BOT_PREFIX = os.getenv('BOT_PREFIX', '!')
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# Channel and Role Names
ROLES = {
    'admin': 'Admin',
    'moderator': 'Moderator', 
    'member': 'Member',
    'bot': 'Bot',
    'english': 'English',
    'russian': 'Russian'
}

# Channel Categories and Channels
CATEGORIES = {
    'server_stats': '📊 SERVER STATS',
    'language_selection': '🌐 LANGUAGE SELECTION',
    # English Categories
    'en_welcome': '👋 WELCOME',
    'en_community': '💬 COMMUNITY',
    'en_trading': '💼 TRADING',
    'en_support': '🛠️ SUPPORT & FEEDBACK',
    # Russian Categories
    'ru_welcome': '👋 ДОБРО ПОЖАЛОВАТЬ',
    'ru_community': '💬 СООБЩЕСТВО',
    'ru_trading': '💼 ТОРГОВЛЯ',
    'ru_support': '🛠️ ПОДДЕРЖКА И ОТЗЫВЫ'
}

CHANNELS = {
    # Global channels
    'total_members': '📊 Total Members: {}',
    'online_members': '🟢 Online Members: {}',
    'choose_language': '🌐-choose-language',
    
    # English channels
    'en_announcements': '📢-announcements',
    'en_status': '🟢-status',
    'en_read_me': '🧠-read-me',
    'en_general': '💬-general',
    'en_cs2_talk': '🎮-cs2-talk',
    'en_skin_chat': '🎨-skin-chat',
    'en_price_discussion': '📉-price-discussion',
    'en_skin_news': '📰-skin-news',
    'en_market': '💸-market',
    'en_looking_for': '🧍-looking-for',
    'en_price_check': '🔍-price-check',
    'en_support': '🆘-support',
    
    # Russian channels
    'ru_announcements': '📢-объявления',
    'ru_status': '🟢-статус',
    'ru_read_me': '🧠-прочти-меня',
    'ru_general': '💬-общий',
    'ru_cs2_talk': '🎮-cs2-обсуждение',
    'ru_skin_chat': '🎨-скины-чат',
    'ru_price_discussion': '📉-обсуждение-цен',
    'ru_skin_news': '📰-новости-скинов',
    'ru_market': '💸-рынок',
    'ru_looking_for': '🧍-ищу-предмет',
    'ru_price_check': '🔍-проверка-цены',
    'ru_support': '🆘-поддержка'
}

# Embed Colors
COLORS = {
    'primary': 0x00ff88,
    'secondary': 0x0099ff,
    'success': 0x00ff00,
    'warning': 0xffaa00,
    'error': 0xff0000,
    'info': 0x00aaff
} 