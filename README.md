# NetGuardian Backend

A Django-based backend system for network traffic monitoring and intelligent throttling using AI-powered profile generation.

## 🎯 Features

- **Real-time Network Monitoring** - WebSocket-based live statistics
- **Intelligent Throttling** - Control bandwidth for specific devices
- **AI Profile Generation** - Use Google Gemini to create optimal network configurations
- **Device Management** - Track and manage network devices
- **Historical Logging** - Store throttle actions and network statistics
- **RESTful API** - Clean API endpoints for frontend integration

## 🏗️ Architecture

- **Django 4.2** with Django REST Framework
- **WebSockets** via Django Channels and Redis
- **Google Gemini AI** for intelligent profile generation
- **SQLite/PostgreSQL** database support
- **Redis** for real-time messaging and channel layers

## 📋 Prerequisites

- Python 3.8+
- Redis server
- Virtual environment (recommended)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd throttle-backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```env
# Security
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=True

# AI Configuration
GEMINI_API_KEY=your-google-gemini-api-key

# Redis Configuration
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# Allowed Hosts (comma-separated)
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Database Setup

```bash
python manage.py migrate
python manage.py createsuperuser  # Optional: for admin access
```

### 4. Start Redis Server

```bash
# Ubuntu/Debian
sudo systemctl start redis

# macOS (via Homebrew)
brew services start redis

# Or run directly
redis-server
```

### 5. Start the Application

**Option A: Production Script**

```bash
python start_production.py
```

**Option B: Manual Start**

```bash
# Terminal 1: Start Django with ASGI
daphne -b 0.0.0.0 -p 8000 netguardian.asgi:application

# Terminal 2: Start Redis listener
python manage.py redis_listener
```

## 🔌 API Endpoints

### Device Control

- `POST /api/throttle/` - Throttle/unthrottle a device
- `GET /api/devices/` - Get current network statistics

### AI Profile Generation

- `POST /api/generate-profile/` - Generate network configuration using AI

### WebSocket

- `ws://localhost:8000/ws/stats/` - Real-time network statistics

## 📡 API Usage Examples

### Throttle a Device

```bash
curl -X POST http://localhost:8000/api/throttle/ \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "192.168.1.100",
    "action": "throttle",
    "limit_mbps": 2.0,
    "reason": "High bandwidth usage"
  }'
```

### Unthrottle a Device

```bash
curl -X POST http://localhost:8000/api/throttle/ \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "192.168.1.100",
    "action": "unthrottle"
  }'
```

### Generate AI Profile

```bash
curl -X POST http://localhost:8000/api/generate-profile/ \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "environment": "home",
      "priority": "gaming",
      "tolerance": "immediately"
    },
    "profile_name": "Gaming Optimized"
  }'
```

## 🗄️ Database Models

- **NetworkDevice** - Store device information and status
- **ThrottleAction** - Log all throttle/unthrottle actions
- **NetworkProfile** - Store AI-generated configurations
- **NetworkStats** - Historical network statistics

## 🔧 Configuration

### Redis Settings

Configure Redis connection in `.env`:

```env
REDIS_HOST=your-redis-host
REDIS_PORT=6379
```

### AI Configuration

Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey):

```env
GEMINI_API_KEY=your-api-key-here
```

### Production Settings

For production deployment:

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## 🧪 Testing

### Test WebSocket Connection

```bash
python test_websocket.py
```

### Test API Endpoints

```bash
# Check server status
curl http://localhost:8000/api/devices/

# Test throttle endpoint
curl -X POST http://localhost:8000/api/throttle/ \
  -H "Content-Type: application/json" \
  -d '{"ip": "192.168.1.100", "action": "throttle"}'
```

## 📊 Admin Interface

Access the Django admin at `http://localhost:8000/admin/` to:

- View and manage network devices
- Review throttle action history
- Manage network profiles
- Monitor network statistics

## 🐛 Troubleshooting

### Redis Connection Issues

```bash
# Check if Redis is running
redis-cli ping

# Start Redis service
sudo systemctl start redis
```

### WebSocket Connection Failed

- Ensure you're using `daphne` (ASGI) not `runserver` (WSGI)
- Check that Redis is running and accessible
- Verify firewall settings for port 8000

### AI Profile Generation Not Working

- Verify `GEMINI_API_KEY` is set correctly
- Check API quota and billing on Google Cloud Console

## 🔒 Security Notes

- Change the default `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Use environment variables for sensitive data
- Consider using PostgreSQL instead of SQLite for production
- Implement proper authentication/authorization as needed

## 📝 Development

### Adding New Features

1. Create models in `api/models.py`
2. Add views in `api/views.py`
3. Update URLs in `api/urls.py`
4. Run migrations: `python manage.py makemigrations && python manage.py migrate`

### Custom Management Commands

Located in `api/management/commands/`:

- `redis_listener.py` - Bridges Redis and WebSocket communications

## 🤝 Integration

This backend is designed to work with:

- Network monitoring tools that publish stats to Redis
- React/Vue.js frontends via REST API and WebSockets
- External throttling engines that subscribe to Redis commands

## 📄 License

[Add your license information here]

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review Django and Redis logs
3. Create an issue in the repository
