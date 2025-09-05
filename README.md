# Enhanced Healthcare Chatbot for Rural India

An AI-powered, multilingual healthcare chatbot designed to enhance access to health information and services for rural and semi-urban populations across India. Supports WhatsApp, SMS, and web channels with real-time government data integration and alerts.

---

## Features

- **Multilingual Support:** 13+ Indian languages including Hindi, Bengali, Telugu, Tamil, Gujarati, Kannada, Malayalam, Marathi, Punjabi, Odia, Assamese, Urdu
- **WhatsApp & SMS Integration:** Via Twilio API, enabling 2-way messaging accessible on basic and smartphones
- **Government Database Integration:** Real-time COVID stats (MOHFW), vaccination centers (CoWIN), health advisories, hospital info
- **Real-Time Alerts:** Automated notifications for vaccinations, disease outbreaks, and health advisories via WhatsApp/SMS
- **Advanced ML/NLP:** Enhanced intent classification, symptom analysis, session context, and confidence-based responses
- **Rural-Friendly UX:** SMS optimization, offline data caching, and easy language switching
- **Deployment Ready:** Containerized with Docker/Docker-compose, built for scalability and monitoring

---

## Technology Stack

- Flask (Python) backend with SQLAlchemy ORM
- PostgreSQL or SQLite database support
- Redis for caching and session management
- Twilio APIs for WhatsApp and SMS messaging
- Google Cloud Translation API for multilingual support
- ML-based chatbot with scikit-learn and TensorFlow
- Prometheus and Grafana for monitoring (optional)

---

## Quick Start

**Prerequisites:**

- Python 3.8+
- Redis server (optional for caching)
- PostgreSQL (recommended for production)
- Twilio account for WhatsApp/SMS integration
- Google Cloud account (optional, for translation API)

**Setup Instructions:**

1. Clone the repository  
git clone https://github.com/your-username/enhanced-healthcare-chatbot.git
cd enhanced-healthcare-chatbot

text

2. Create and activate a virtual environment  
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate

text

3. Install dependencies  
pip install -r requirements.txt

text

4. Copy and edit environment variables  
cp .env.example .env

Edit .env to add API keys and secrets
text

5. Initialize the database  
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

text

6. Run the chatbot app  
python run.py

text

7. Access the web interface at [http://localhost:5000](http://localhost:5000)

---

## WhatsApp and SMS Setup

- Register for Twilio account: https://twilio.com  
- Apply for WhatsApp Business API access  
- Purchase phone number for SMS  
- Update `.env` with credentials and phone numbers  
- Configure webhook URLs in Twilio Console:  
- WhatsApp: `/webhook/whatsapp`  
- SMS: `/webhook/sms`

---

## APIs Provided

- `/api/health-data/covid-stats`  
- `/api/health-data/vaccination-centers`  
- `/api/translate` (POST)  
- `/api/languages`  
- `/api/chat/enhanced` (POST)  

---

## Contributing

- Follow PEP 8 coding style  
- Add tests with pytest  
- Update documentation  
- Submit PR for review

---

## License

MIT License - see LICENSE file

---

Made with ❤️ to improve healthcare awareness and access in rural India.

---

## Support

For issues or assistance, please create an issue or contact the development team.