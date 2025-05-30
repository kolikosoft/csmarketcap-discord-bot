# CSMarketCap Discord Bot

A comprehensive Discord bot for CS2 skin trading communities with bilingual support (English/Russian), advanced permission management, and complete server automation.

## 🎯 Features

### **Admin-Only Command System**
- **ALL bot commands restricted to Admin role only**
- Moderators can manage server but cannot control bot
- Comprehensive permission hierarchy

### **Bilingual Server Structure**
- **English/Russian language-based channel visibility**
- Automatic role assignment with language selection
- Language-specific welcome messages and DMs
- Separate support systems for each language

### **Advanced Permission Management**
- **Welcome categories**: READ-ONLY for users
- **Community categories**: Users can write (general chat, discussions)
- **Trading categories**: Users can write (market, trading)
- **Support categories**: READ-ONLY except ticket buttons
- **Very restrictive user permissions** (no embed links, file attachments, voice)

### **Support Ticket System**
- Private thread creation with cooldown protection
- Automatic staff addition to tickets
- Duplicate ticket prevention
- Language-specific ticket handling
- Rate limit protection

### **Live Statistics**
- Auto-updating voice channels with member counts
- Real-time online/offline statistics
- Background task updating every 10 seconds

### **Complete Server Automation**
- Fresh server setup with `!fresh` command
- Standard setup with `!setup` command
- Automatic new member handling
- Persistent button views (survive bot restarts)

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8 or higher
- Discord bot token
- Server with appropriate permissions

### 2. Installation
```bash
# Clone or download the bot files
cd csmarketcap-bot

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### 3. Configuration
Edit `.env` file:
```env
DISCORD_TOKEN=your_bot_token_here
GUILD_ID=your_server_id_here
BOT_PREFIX=!
DEBUG_MODE=True
```

### 4. Run the Bot
```bash
python bot.py
```

## 🔧 Setup Commands (Admin Only)

### **Fresh Server Setup**
```
!fresh
```
- **COMPLETELY WIPES** the server
- Deletes all channels and roles
- Recreates entire server structure
- **Requires CONFIRM within 30 seconds**

### **Standard Setup**
```
!setup
```
- Creates all roles and channels
- Sets up permissions
- Configures language selection
- Sets up support ticket systems

### **Server Cleanup**
```
!cleanup
```
- Removes bot-created channels and roles
- Preserves existing server structure
- Useful for clean reinstallation

### **Manual Language Setup**
```
!language
```
- Manually setup language selection channel
- Useful if language buttons stop working

## 📊 Information Commands (Admin Only)

### **Bot Information**
```
!info
```
- Bot statistics and version info
- Server count and member count
- Feature overview

### **Server Statistics**
```
!stats
```
- Member count breakdown
- Language distribution
- Server structure statistics

### **Help**
```
!help
```
- Complete command list
- Usage instructions
- Important notes

## 🏗️ Server Structure

### **Visible to Everyone**
```
📊 SERVER STATS
├── 📊 Total Members: X (voice)
└── 🟢 Online Members: X (voice)

🌐 LANGUAGE SELECTION
└── 🌐-choose-language
```

### **English Channels** (English role only)
```
👋 WELCOME (READ-ONLY)
├── 📢-announcements
├── 🟢-status
└── 🧠-read-me

💬 COMMUNITY (USERS CAN WRITE)
├── 💬-general
├── 🎮-cs2-talk
├── 🎨-skin-chat
├── 📉-price-discussion
└── 📰-skin-news

💼 TRADING (USERS CAN WRITE)
├── 💸-market
├── 🧍-looking-for
└── 🔍-price-check

🛠️ SUPPORT & FEEDBACK (READ-ONLY + ticket button)
└── 🆘-support
```

### **Russian Channels** (Russian role only)
```
👋 ДОБРО ПОЖАЛОВАТЬ (READ-ONLY)
├── 📢-объявления
├── 🟢-статус
└── 🧠-прочти-меня

💬 СООБЩЕСТВО (USERS CAN WRITE)
├── 💬-общий
├── 🎮-cs2-обсуждение
├── 🎨-скины-чат
├── 📉-обсуждение-цен
└── 📰-новости-скинов

💼 ТОРГОВЛЯ (USERS CAN WRITE)
├── 💸-рынок
├── 🧍-ищу-предмет
└── 🔍-проверка-цены

🛠️ ПОДДЕРЖКА И ОТЗЫВЫ (READ-ONLY + ticket button)
└── 🆘-поддержка
```

## 👥 Role System

### **Role Hierarchy**
1. **Admin** (Red)
   - Full server permissions
   - **ONLY role that can use bot commands**
   - Can manage everything

2. **Moderator** (Orange)
   - Manage messages, channels, members
   - Kick/ban permissions
   - **CANNOT use bot commands**

3. **Bot** (Blue)
   - Bot management permissions
   - Thread and message management

4. **Member** (Green)
   - Very restrictive base permissions
   - Read messages, send messages, reactions only
   - NO embed links, file attachments, voice

5. **English** (Blue)
   - Language role for English speakers
   - Access to English channels only

6. **Russian** (Yellow)
   - Language role for Russian speakers  
   - Access to Russian channels only

## 🎫 Support Ticket System

### **Features**
- **5-second cooldown** to prevent spam
- **Duplicate prevention** - one ticket per user
- **Private threads** with automatic staff addition
- **Language-specific** ticket handling
- **Rate limit protection** when adding users

### **How It Works**
1. User clicks ticket button in support channel
2. Bot creates private thread
3. Automatically adds all admins and moderators
4. User gets confirmation message
5. Staff can close ticket with close button

## 🔒 Permission Structure

### **Channel Types**
- **Welcome**: Users can only read (announcements, info)
- **Community**: Users can read and write (chat, discussions)
- **Trading**: Users can read and write (market, trading)
- **Support**: Users can only read and use ticket buttons

### **User Restrictions**
- **NO embed links** (prevents link previews)
- **NO file attachments** (prevents file sharing)
- **NO voice permissions** (cannot join/speak in voice)
- **NO external emoji usage**
- **NO mention everyone** permissions

### **Admin Controls**
- **Only Admins** can use bot commands
- **Moderators** can manage server but not bot
- **Clear permission hierarchy**

## 🌐 Language System

### **Language Selection**
- New members see language selection channel
- Buttons assign appropriate language role
- **5-second cooldown** to prevent spam
- Switching languages removes old role

### **Features**
- **DM welcome guide** in selected language
- **Channel access** based on language role
- **Support tickets** in appropriate language
- **Bilingual button labels** and messages

## 📈 Live Statistics

### **Auto-Updating Channels**
- Total member count (voice channel)
- Online member count (voice channel)
- Updates every 10 seconds
- Handles multiple servers

## 🛡️ Error Handling

### **Comprehensive Protection**
- **Rate limit protection** for Discord API
- **Graceful error handling** with try/catch blocks
- **Cooldown systems** for button interactions
- **Permission checks** before operations
- **Logging system** for debugging

### **Safety Features**
- **Confirmation required** for dangerous operations
- **Protected roles** cannot be deleted
- **Timeout handling** for user confirmations
- **Duplicate prevention** for tickets and roles

## 🔧 Technical Details

### **Dependencies**
- `discord.py 2.3.0+` - Discord API wrapper
- `python-dotenv` - Environment variable management
- `asyncio` - Asynchronous operations

### **Key Features**
- **Persistent views** - Buttons work after bot restart
- **Background tasks** - Live statistics updating
- **Timezone-aware** datetime handling
- **Modular architecture** - Separated concerns
- **Comprehensive logging** - Debug and error tracking

### **File Structure**
```
csmarketcap-bot/
├── bot.py           # Main bot file
├── config.py        # Configuration and constants
├── utils.py         # Utility functions
├── views.py         # Discord UI components
├── requirements.txt # Dependencies
├── .env.example     # Environment template
└── README.md        # This file
```

## 🚨 Important Notes

### **Before Running**
1. **Create Admin role** manually and assign to yourself
2. **Set bot permissions** in Discord Developer Portal
3. **Configure .env file** with proper tokens
4. **Invite bot** with Administrator permissions

### **Required Bot Permissions**
- Administrator (recommended) OR:
  - Manage Roles
  - Manage Channels
  - Manage Messages
  - Create Threads
  - Send Messages
  - Read Messages
  - Add Reactions
  - Use External Emojis

### **Security**
- **All commands are Admin-only** by design
- **Moderators cannot control bot** - only server management
- **Users have very restrictive permissions**
- **Protected from common attack vectors**

## 🆘 Troubleshooting

### **Bot Won't Start**
- Check `DISCORD_TOKEN` in `.env` file
- Verify bot has proper permissions
- Check Python version (3.8+ required)

### **Commands Not Working**
- Ensure you have **Admin role** (exact name match)
- Bot needs **Administrator permissions**
- Check for typos in commands

### **Buttons Not Working**
- Bot may need restart to register persistent views
- Check bot permissions in channels
- Verify roles exist before setup

### **Permissions Issues**
- Run `!fresh` to completely reset server
- Ensure bot role is **above** all managed roles
- Check Discord's role hierarchy

## 📞 Support

If you encounter issues:
1. Check the console logs for error messages
2. Verify all requirements are met
3. Try `!fresh` command to reset everything
4. Check Discord permissions and role hierarchy

## 📄 License

This project is provided as-is for educational and community purposes. Feel free to modify and adapt for your community's needs.

---

**CSMarketCap Discord Bot** - Complete CS2 Trading Community Automation 🎮 