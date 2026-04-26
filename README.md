# NetGuardian Backend

A Django-based backend system for network traffic monitoring and intelligent throttling using AI-powered profile generation.

## 🎯 Features

- **Real-time Network Monitoring** - WebSocket-based live statistics
- **Intelligent Throttling** - Control bandwidth for specific devices
- **AI Profile Generation** - Use Google Gemini to create optimal network configurations
- **Device Management** - Track and manage network devices
- **Historical Logging** - Store throttle actions and network statistics
- **RESTful API** - Clean API endpoints for frontend integration
- **Distributed Architecture** - Backend can run separately from network engine
- **Cross-Device Communication** - Redis-based messaging between components

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
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,10.42.0.137
```

**For Distributed Deployment**: If running the backend on a separate machine from the network engine:

```env
# Backend Machine IP Configuration
REDIS_HOST=127.0.0.1          # Redis runs locally on backend machine
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,<backend-ip>

# Configure network engine to connect to backend's Redis
# On network engine machine, set:
# REDIS_HOST=<backend-machine-ip>  # e.g., 10.42.0.137
# REDIS_PORT=6379
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

**For Distributed Setup**: If your network engine runs on a different machine (like a router), configure Redis to accept remote connections:

```bash
# Configure Redis to bind to all interfaces
sudo sed -i 's/bind 127.0.0.1 -::1/bind 0.0.0.0/' /etc/redis/redis.conf

# Disable protected mode for local network access
redis-cli CONFIG SET protected-mode no
redis-cli CONFIG REWRITE

# Restart Redis
sudo systemctl restart redis-server

# Test from remote machine
redis-cli -h <this-machine-ip> -p 6379 ping
```

### 5. Start the Application

**Option A: Production Script**

```bash
python start_production.py
```

**Option B: Manual Start**

```bash
# Terminal 1: Start Django with ASGI
daphne -b 0.0.0.0 -p 8082 netguardian.asgi:application

# Terminal 2: Start Redis listener
python manage.py redis_listener
```

## 🔌 API Endpoints

### System Status

- `GET /api/health/` - System health check and service status

### Device Control

- `POST /api/throttle/` - Throttle/unthrottle a device
- `GET /api/devices/` - Get current network statistics

### AI Profile Generation

- `POST /api/generate-profile/` - Generate network configuration using AI

### WebSocket

- `ws://localhost:8082/ws/stats/` - Real-time network statistics (**Note: trailing slash is required!**)


```bash
curl -s http://localhost:8082/api/health/ | python3 -m json.tool
# Returns: {"status":"healthy","services":{"database":"connected","redis":"connected","ai_generation":"configured"}}
```


```bash
curl -X POST http://localhost:8082/api/throttle/ \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "10.42.0.140",
    "action": "throttle",
    "limit_mbps": 2.0,
    "reason": "High bandwidth usage"
  }'
```

### Unthrottle a Device

```bash
curl -X POST http://localhost:8082/api/throttle/ \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "10.42.0.140",
    "action": "unthrottle"
  }'
```

### Generate AI Profile

```bash
curl -X POST http://localhost:8082/api/generate-profile/ \
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
# Install websockets if needed
pip install websockets

# Test WebSocket (requires ASGI server)
python test_websocket.py
```

### Test API Endpoints

```bash
# Check system health
curl -s http://localhost:8082/api/health/ | python3 -m json.tool

# Check current network stats
curl -s http://localhost:8082/api/devices/ | python3 -m json.tool

# Test throttle endpoint (use real IP from your network)
curl -X POST http://localhost:8082/api/throttle/ \
  -H "Content-Type: application/json" \
  -d '{"ip": "10.42.0.140", "action": "throttle", "limit_mbps": 2}'
```

## 📊 Admin Interface

Access the Django admin at `http://localhost:8082/admin/` to:

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

# For remote engine connections, configure Redis to bind to all interfaces
sudo sed -i 's/bind 127.0.0.1 -::1/bind 0.0.0.0/' /etc/redis/redis.conf
redis-cli CONFIG SET protected-mode no
redis-cli CONFIG REWRITE
sudo systemctl restart redis-server
```

### WebSocket Connection Failed

- Ensure you're using `daphne` (ASGI) not `runserver` (WSGI)
- Check that Redis is running and accessible
- Verify firewall settings for port 8082
- **Important**: WebSocket URL must include trailing slash: `ws://localhost:8082/ws/stats/` (not `/ws/stats`)
- **CORS Issues**: If connecting from a frontend on a different origin (e.g., `localhost:5173`), the `AllowedHostsOriginValidator` in `netguardian/asgi.py` has been removed to allow cross-origin WebSocket connections

### No Network Stats Appearing

- Verify your network engine is running and configured to connect to this Redis server
- Check engine configuration: `REDIS_HOST=<this-laptop-ip>` and `REDIS_PORT=6379`
- Monitor Redis activity: `redis-cli MONITOR`
- Check subscribers: `redis-cli PUBSUB NUMSUB network-stats throttle-commands`

### AI Profile Generation Not Working

- Verify `GEMINI_API_KEY` is set correctly in `.env`
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

- **Network monitoring engines** that publish stats to Redis (`network-stats` channel)
- **React/Vue.js frontends** via REST API and WebSockets
- **External throttling engines** that subscribe to Redis commands (`throttle-commands` channel)

### For Network Engine Integration

Your network monitoring engine should:

1. **Connect to Redis** on this backend server
2. **Publish network stats** to `network-stats` channel in JSON format:
   ```json
   {
     "timestamp": 1234567890.123,
     "global": { "total_down_mbps": 25.5, "total_up_mbps": 5.2 },
     "devices": [
       {
         "ip": "10.42.0.140",
         "mac": "aa:bb:cc:dd:ee:ff",
         "hostname": "device-name",
         "down_mbps": 15.3,
         "up_mbps": 2.1,
         "status": "normal"
       }
     ],
     "events": ["[10:42:15] Throttled 10.42.0.140"]
   }
   ```
3. **Subscribe to throttle commands** from `throttle-commands` channel
4. **Apply throttling rules** using iptables/tc based on received commands

## � Quick Operation Commands

### System Status

```bash
# Check overall system health
curl -s http://localhost:8082/api/health/ | python3 -m json.tool

# View current network activity
curl -s http://localhost:8082/api/devices/ | python3 -m json.tool

# Check Redis subscriber status
redis-cli PUBSUB NUMSUB network-stats throttle-commands
```

### Device Control

```bash
# Throttle a high-usage device
curl -X POST http://localhost:8082/api/throttle/ \
  -H "Content-Type: application/json" \
  -d '{"ip":"10.42.0.140","action":"throttle","limit_mbps":2}'

# Unthrottle a device
curl -X POST http://localhost:8082/api/throttle/ \
  -H "Content-Type: application/json" \
  -d '{"ip":"10.42.0.140","action":"unthrottle"}'
```

### Real-time Monitoring

```bash
# Watch live network stats via Redis
redis-cli SUBSCRIBE network-stats

# Test WebSocket connection
python test_websocket.py

# Monitor Redis activity
redis-cli MONITOR
```

## �📄 License

[Add your license information here]

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review Django and Redis logs
3. Create an issue in the repository
