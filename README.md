# CollaLearn 🎓

**AI-Powered Collaborative Study Rooms on Telegram**

CollaLearn is a production-ready Telegram bot that enables students to create collaborative study spaces, share materials, and leverage AI for enhanced learning.

---

## ✨ Features

### 📚 Study Room Management
- Create private study rooms with unique codes
- Join existing rooms by code
- Support for both private chats and Telegram groups
- Room linking for group collaboration

### 📎 File Management
- Upload any file type (PDFs, images, documents)
- Files stored using Telegram's file_id (no external storage needed)
- Smart tagging system (manual + AI-suggested tags)
- Organized by room for easy management

### 🔍 Smart Search
- Search files by tags, filename, or content
- Scoped to current room for relevant results
- Pagination support for large result sets

### 🤖 AI-Powered Features
- **Summarize**: Get concise summaries of study materials
- **Explain**: Simplify complex concepts
- **Quiz**: Generate multiple-choice questions for practice
- AI-suggested tags for automatic file organization
- Rate limiting to prevent abuse

### 👥 Group Integration
- Add bot to Telegram groups
- Link groups to study rooms
- All features work seamlessly in group chats
- Admin-only room linking for security

### 🛡️ Admin Panel
- Web-based dashboard
- User management (view, update roles)
- Room management (view, deactivate)
- File browsing
- System statistics
- Configuration viewing

---

## 🏗️ Architecture

```
CollaLearn
├── Telegram Bot (python-telegram-bot)
│   ├── User Management
│   ├── Room System
│   ├── File Handling
│   ├── AI Integration
│   └── Search Engine
├── Admin Panel (FastAPI)
│   ├── Dashboard
│   ├── User Management
│   ├── Room Management
│   ├── File Browser
│   └── Settings
└── Database (MongoDB)
    ├── users
    ├── rooms
    ├── files
    ├── ai_usage
    └── settings
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- MongoDB 4.4 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Perplexity API Key (or compatible LLM API)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/collalearn.git
cd collalearn
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
nano .env  # Edit with your actual values
```

Required environment variables:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
MONGODB_URI=mongodb://localhost:27017
AI_API_KEY=your_perplexity_api_key_here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password_here
ADMIN_SECRET_KEY=your_random_secret_key_here
```

5. **Start MongoDB** (if not already running)
```bash
sudo systemctl start mongod
# OR
sudo service mongodb start
```

6. **Run the application**
```bash
python main.py
```

The bot will start in polling mode and the admin panel will be available at `http://localhost:8000/admin`

---

## 📱 Bot Commands

### Basic Commands
- `/start` - Initialize bot and register user
- `/help` - Display help message with all commands

### Room Management
- `/create_room` - Create a new study room
- `/join_room <CODE>` - Join existing room with code
- `/my_room` - View current room information
- `/leave_room` - Leave current room

### File & Search
- **Send any file** - Upload to current room
- `/add_tags tag1, tag2` - Reply to file to add tags
- `/search <query>` - Search files in current room

### AI Features
- `/summarise` or `/summarize` - Reply to content for summary
- `/explain` - Reply to content for simple explanation
- `/quiz [number]` - Generate MCQs (default: 5 questions)

### Group Commands (Admin only)
- `/connect_room <CODE>` - Link group to study room
- `/disconnect_room` - Unlink group from room

---

## 🖥️ Admin Panel

Access the admin panel at `http://your-server:8000/admin`

**Default credentials:**
- Username: `admin`
- Password: (set in `.env` file)

### Admin Features

#### Dashboard
- Total users, rooms, files statistics
- AI usage metrics

#### User Management
- View all users
- Change user roles (user/admin)
- View user activity

#### Room Management
- View all rooms
- See member counts
- Deactivate rooms
- View linked groups

#### File Browser
- View all uploaded files
- Filter by room
- See tags and metadata

#### Settings
- View AI configuration
- Check rate limits
- System information

---

## 🐳 Deployment (VPS)

### Using systemd (Recommended for Production)

1. **Create systemd service file**
```bash
sudo nano /etc/systemd/system/collalearn.service
```

```ini
[Unit]
Description=CollaLearn Telegram Bot
After=network.target mongod.service

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/collalearn
Environment="PATH=/path/to/collalearn/venv/bin"
ExecStart=/path/to/collalearn/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. **Enable and start service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable collalearn
sudo systemctl start collalearn
```

3. **Check status**
```bash
sudo systemctl status collalearn
sudo journalctl -u collalearn -f  # View logs
```

### Using Docker (Alternative)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  collalearn:
    build: .
    ports:
      - "8000:8000"
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - MONGODB_URI=mongodb://mongo:27017
      - AI_API_KEY=${AI_API_KEY}
    depends_on:
      - mongo
    restart: unless-stopped

  mongo:
    image: mongo:6
    volumes:
      - mongo_data:/data/db
    restart: unless-stopped

volumes:
  mongo_data:
```

---

## 🔧 Configuration

### AI Provider

CollaLearn uses Perplexity API by default but can work with any OpenAI-compatible API:

```env
# For OpenAI
AI_API_URL=https://api.openai.com/v1/chat/completions
AI_MODEL=gpt-3.5-turbo
AI_API_KEY=sk-...

# For Perplexity
AI_API_URL=https://api.perplexity.ai/chat/completions
AI_MODEL=llama-3.1-sonar-small-128k-online
AI_API_KEY=pplx-...

# For other providers
AI_API_URL=https://your-provider.com/v1/chat/completions
AI_MODEL=model-name
AI_API_KEY=your-key
```

### Rate Limiting

Control AI usage per user:
```env
AI_CALLS_PER_USER_PER_DAY=50
```

---

## 📊 Database Schema

### Users Collection
```json
{
  "user_id": 123456789,
  "username": "student123",
  "first_name": "John",
  "last_name": "Doe",
  "current_room_code": "ABC12345",
  "role": "user",
  "created_at": "2025-01-01T00:00:00"
}
```

### Rooms Collection
```json
{
  "code": "ABC12345",
  "name": "Physics Study Group",
  "description": "Preparing for finals",
  "owner_id": 123456789,
  "members": [123456789, 987654321],
  "linked_chat_id": -1001234567890,
  "is_active": true,
  "created_at": "2025-01-01T00:00:00"
}
```

### Files Collection
```json
{
  "file_id": "AgACAgIAAxk...",
  "file_type": "document",
  "file_name": "chapter1.pdf",
  "caption": "Physics Chapter 1",
  "uploader_id": 123456789,
  "room_code": "ABC12345",
  "tags": ["physics", "chapter1"],
  "ai_tags": ["mechanics", "kinematics"],
  "message_id": 123,
  "created_at": "2025-01-01T00:00:00"
}
```

---

## 🛠️ Development

### Project Structure
```
collalearn/
├── main.py                 # Application entry point
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── bot/                   # Telegram bot module
│   ├── handlers/         # Command handlers
│   ├── models/           # Data models
│   └── services/         # Business logic
├── admin/                # Admin panel module
│   ├── routes.py        # API endpoints
│   ├── auth.py          # Authentication
│   └── templates/       # HTML templates
└── db/                   # Database module
    └── mongo.py         # MongoDB connection
```

### Adding New Features

1. **Create new handler** in `bot/handlers/`
2. **Add service logic** in `bot/services/`
3. **Register handler** in `main.py`
4. **Update documentation**

### Running Tests
```bash
# Unit tests (to be implemented)
pytest tests/

# Coverage
pytest --cov=bot --cov=admin tests/
```

---

## 🐛 Troubleshooting

### Bot not responding
- Check bot token is correct
- Verify MongoDB is running
- Check logs: `journalctl -u collalearn -f`

### Admin panel not accessible
- Check port 8000 is open
- Verify firewall rules
- Check admin credentials in `.env`

### AI commands failing
- Verify AI API key is valid
- Check API rate limits
- Review AI provider status

### Database connection errors
- Ensure MongoDB is running
- Check MONGODB_URI in `.env`
- Verify network connectivity

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📧 Support

For issues and questions:
- GitHub Issues: [github.com/yourusername/collalearn/issues](https://github.com/yourusername/collalearn/issues)
- Telegram: @yoursupport

---

## 🙏 Acknowledgments

- python-telegram-bot library
- FastAPI framework
- MongoDB database
- Perplexity AI
- Bootstrap UI framework

---

**Built with ❤️ for students worldwide**