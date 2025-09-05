# run.py - Modified for deployment compatibility
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Your existing imports (add your actual imports here)
# from your_modules import your_blueprints, your_models, etc.

def create_app():
    """Application factory pattern for better deployment compatibility"""
    app = Flask(__name__)
    
    # Configuration based on environment
    if os.environ.get('VERCEL'):
        # Vercel (Serverless) configuration
        app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///healthcare_bot.db')
        app.config['REDIS_URL'] = os.environ.get('REDIS_URL')
    elif os.environ.get('RENDER'):
        # Render configuration
        app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL')
        app.config['REDIS_URL'] = os.environ.get('REDIS_URL')
    else:
        # Local development configuration
        app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///healthcare_bot.db')
        app.config['REDIS_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Common Flask configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # API Keys and external services
    app.config['TWILIO_ACCOUNT_SID'] = os.environ.get('TWILIO_ACCOUNT_SID')
    app.config['TWILIO_AUTH_TOKEN'] = os.environ.get('TWILIO_AUTH_TOKEN')
    app.config['TWILIO_PHONE_NUMBER'] = os.environ.get('TWILIO_PHONE_NUMBER')
    app.config['TWILIO_WHATSAPP_NUMBER'] = os.environ.get('TWILIO_WHATSAPP_NUMBER')
    app.config['GOOGLE_TRANSLATE_API_KEY'] = os.environ.get('GOOGLE_TRANSLATE_API_KEY')
    
    # Government API endpoints
    app.config['MOHFW_API_URL'] = os.environ.get('MOHFW_API_URL', 'https://api.covid19india.org/data.json')
    app.config['COWIN_API_URL'] = os.environ.get('COWIN_API_URL', 'https://cdn-api.co-vin.in/api')
    
    # Initialize extensions
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    
    # Redis setup with fallback for serverless environments
    try:
        import redis
        if app.config['REDIS_URL']:
            redis_client = redis.from_url(app.config['REDIS_URL'])
            redis_client.ping()
            app.redis = redis_client
        else:
            app.redis = None
    except:
        app.redis = None
        if not os.environ.get('VERCEL'):
            app.logger.warning("Redis not available, using in-memory storage")
    
    # Import and register your existing blueprints/routes
    # Replace these with your actual imports:
    try:
        # Example imports - replace with your actual module structure:
        # from routes.api import api_bp
        # from routes.webhook import webhook_bp  
        # from routes.main import main_bp
        # 
        # app.register_blueprint(api_bp, url_prefix='/api')
        # app.register_blueprint(webhook_bp, url_prefix='/webhook')
        # app.register_blueprint(main_bp)
        
        # Placeholder - replace with your actual route registrations
        pass
    except ImportError as e:
        app.logger.warning(f"Could not import blueprints: {e}")
    
    # Health check endpoint for deployment platforms
    @app.route('/health')
    def health_check():
        return {"status": "healthy", "message": "Healthcare Chatbot API is running"}, 200
    
    # Basic route if no other routes are loaded
    @app.route('/')
    def home():
        return {"message": "Healthcare Chatbot API", "status": "running"}
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Endpoint not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500
    
    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    # For local development
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
