# 🌾 CropGPT - Farmer Assistant

A comprehensive bilingual agricultural assistant for farmers in Jharkhand, providing AI-powered farming advice, real-time crop prices, weather forecasts, and government scheme information.

## 🌟 Features

### 🤖 AI Chatbot Assistant
- **Bilingual Support**: Natural conversations in Hindi and English
- **Voice Interaction**: Speak in Hindi or English and hear responses
- **Fine-tuned LLM**: Agricultural knowledge using Llama-2 with QLoRA
- **Context-Aware**: Understands farming-specific queries
- **Quick Suggestions**: Pre-defined questions for common topics
- **Voice Commands**: Control app with voice (clear chat, switch language, etc.)

### 💰 Crop Prices Dashboard
- **Real-time Data**: Daily prices from Jharkhand mandis
- **Market Coverage**: Ranchi, Jamshedpur, Dhanbad, Bokaro, and more
- **Price Trends**: Historical data with interactive charts
- **Price Alerts**: Personalized notifications for target prices

### 🌤️ Weather Forecast
- **7-Day Forecast**: Agricultural weather insights
- **Farming Advice**: Irrigation and harvesting recommendations
- **Location-Specific**: Tailored for Jharkhand region
- **Weather Alerts**: Warnings for adverse conditions

### 🏛️ Government Schemes Portal
- **Comprehensive Database**: Central and state government schemes
- **Application Links**: Direct access to application portals
- **Eligibility Calculator**: Personalized scheme recommendations
- **Document Assistance**: Required documents and forms

### 📱 User-Friendly Interface
- **Responsive Design**: Works seamlessly on mobile and desktop
- **Language Toggle**: Switch between Hindi and English
- **Accessibility**: Optimized for rural internet connections
- **Offline Support**: Cached content for offline access

## 🏗️ Architecture

### Backend Technology Stack
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with Redis caching
- **LLM**: Llama-2-7B with QLoRA fine-tuning
- **APIs**: Agmarknet, OpenWeatherMap, Digital India
- **Containerization**: Docker with docker-compose

### Frontend Technology Stack
- **Core**: HTML5, CSS3, JavaScript (vanilla)
- **Styling**: Tailwind CSS with Devanagari font support
- **Internationalization**: i18next for bilingual support
- **Charts**: Chart.js for data visualization
- **Icons**: Font Awesome

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for development)
- PostgreSQL client (optional)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/cropgpt.git
   cd cropgpt
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application**
   ```bash
   # Development mode
   docker-compose up -d

   # Production mode
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

4. **Access the application**
   - Frontend: http://localhost
   - API Documentation: http://localhost/docs
   - Admin Panel: http://localhost:5050 (optional)

### Environment Configuration

Create a `.env` file with the following variables:

```env
# Application Settings
DEBUG=true
ENVIRONMENT=development
SECRET_KEY=your-super-secret-key

# Database Configuration
DB_PASSWORD=secure_password
REDIS_PASSWORD=redis_password

# API Keys
OPENWEATHER_API_KEY=your_openweather_key
AGMARKNET_API_KEY=your_agmarknet_key
DIGITAL_INDIA_API_KEY=your_digital_india_key

# LLM Configuration
HUGGINGFACE_TOKEN=your_huggingface_token
```

## 📊 Database Schema

The application uses PostgreSQL with the following main tables:

- **users**: Farmer profiles and preferences
- **chat_conversations**: AI assistant interactions
- **crop_prices**: Daily market price data
- **weather_data**: Weather forecasts and observations
- **government_schemes**: Farmer welfare schemes
- **user_scheme_applications**: Scheme application tracking

For detailed schema information, see `database/migrations/001_initial_schema.sql`.

## 🤖 LLM Training

### Dataset Preparation
Create a JSONL file with agricultural Q&A pairs:

```jsonl
{"text": "<s>[INST] What fertilizer for paddy? [/INST] For paddy, use 50-60 kg/acre urea, 25-30 kg/acre DAP...</s>", "language": "en", "category": "fertilizer"}
{"text": "<s>[INST] धान के लिए कौन सा उर्वरक? [/INST] धान के लिए 50-60 किग्रा/एकड़ यूरिया...</s>", "language": "hi", "category": "fertilizer"}
```

### Training Command
```bash
cd backend
python llm/train.py
```

The training script will:
- Load Llama-2-7B with 4-bit quantization
- Apply QLoRA fine-tuning
- Save the model to `/app/models/finetuned_llama2`

## 📱 API Documentation

### Chat Endpoints
```http
POST /api/chat
{
  "message": "What is the best fertilizer for paddy?",
  "language": "hi",
  "session_id": "session_12345"
}
```

### Prices Endpoints
```http
GET /api/prices/current?market=Ranchi&commodity=Paddy
GET /api/prices/history?commodity=Paddy&days=30
```

### Weather Endpoints
```http
GET /api/weather/current
GET /api/weather/forecast
```

### Schemes Endpoints
```http
GET /api/schemes?category=financial_assistance
GET /api/schemes/search?query=किसान
```

## 🧪 Development

### Local Development Setup

1. **Backend Development**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend Development**
   ```bash
   cd frontend
   # Serve static files with your preferred web server
   python -m http.server 3000
   ```

3. **Database Setup**
   ```bash
   # Start PostgreSQL and Redis
   docker-compose up db redis -d

   # Run migrations
   psql -h localhost -U cropgpt_user -d cropgpt -f database/migrations/001_initial_schema.sql
   ```

### Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests (if implemented)
cd frontend
npm test  # or your test runner
```

### Code Quality
```bash
# Backend linting
cd backend
black .
flake8 .
mypy .

# Frontend linting (if implemented)
cd frontend
npm run lint
```

## 📁 Project Structure

```
cropgpt/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core configuration
│   │   ├── db/                # Database utilities
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   └── utils/             # Utility functions
│   ├── llm/                   # LLM training and inference
│   ├── scripts/               # Data fetching scripts
│   └── tests/                 # Backend tests
├── frontend/                   # Web frontend
│   ├── static/
│   │   ├── css/               # Stylesheets
│   │   ├── js/                # JavaScript modules
│   │   └── images/            # Static assets
│   ├── locales/               # Language files
│   └── templates/             # HTML templates
├── database/                   # Database configuration
│   ├── migrations/            # SQL migration files
│   └── seeds/                 # Sample data
├── docker/                     # Docker configurations
├── docs/                       # Documentation
└── scripts/                    # Utility scripts
```

## 🔧 Configuration

### Database Configuration
- **PostgreSQL**: Primary data storage
- **Redis**: Caching and session storage
- **Connection Pooling**: Optimized for concurrent requests

### API Rate Limits
- **Default**: 100 requests per minute per IP
- **Chat Endpoint**: 30 requests per minute per user
- **Data Endpoints**: 60 requests per minute per IP

### Caching Strategy
- **Prices**: 30 minutes cache
- **Weather**: 15 minutes cache
- **Schemes**: 24 hours cache
- **Chat**: No caching (real-time responses)

## 🌐 Deployment

### Production Deployment

1. **Server Requirements**
   - **CPU**: 4 cores minimum
   - **RAM**: 8GB minimum
   - **Storage**: 50GB SSD
   - **GPU**: 16GB VRAM (for LLM inference)

2. **Docker Deployment**
   ```bash
   # Production deployment
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

3. **SSL Configuration**
   ```bash
   # Use Let's Encrypt certificates
   certbot --nginx -d yourdomain.com
   ```

### Monitoring Setup
- **Health Checks**: `/health` endpoint
- **Logging**: Structured JSON logs
- **Metrics**: Prometheus-compatible metrics
- **Error Tracking**: Sentry integration

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Add tests for new features
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Documentation**: [docs/](docs/) directory
- **API Reference**: http://localhost/docs
- **Issues**: [GitHub Issues](https://github.com/your-org/cropgpt/issues)

### Contact Information
- **Email**: support@cropgpt.in
- **Helpline**: +91-XXXXXXXXXX
- **Office**: Ranchi, Jharkhand, India

## 🙏 Acknowledgments

- **Llama-2**: Meta AI for the base language model
- **Agmarknet**: Government of India for crop price data
- **IMD**: India Meteorological Department for weather data
- **Digital India**: Government portal for scheme information

## 📈 Roadmap

### Phase 1 (Current)
- ✅ Basic AI chatbot functionality
- ✅ Crop prices integration
- ✅ Weather forecast integration
- ✅ Government schemes database
- ✅ Bilingual support (Hindi/English)

### Phase 2 (Planned)
- 📱 Mobile application (Android)
- 🔄 Real-time price alerts
- 📊 Advanced analytics dashboard
- 🌾 Crop disease detection
- 💬 Voice support in Hindi

### Phase 3 (Future)
- 🤝 Multi-language support (more Indian languages)
- 🎯 Personalized recommendations
- 📈 Market trend predictions
- 🤖 Advanced AI features
- 🌐 Integration with agricultural IoT devices

---

**Made with ❤️ for farmers in Jharkhand**

*Empowering farmers with technology and knowledge*