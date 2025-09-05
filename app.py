# This file should be named app.py and placed in your project root
# It's the entry point for both Vercel and Render deployments

import os
import sys

# Add the current directory to Python path so we can import your existing modules
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Try to import your existing app from run.py
    from run import app
except ImportError:
    try:
        # Alternative: try importing from main module or app factory
        from main import app  # or wherever your app is defined
    except ImportError:
        # If neither works, create a basic app structure
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from flask_migrate import Migrate
        import redis
        
        def create_app():
    app = Flask(__name__)
    
    # Configuration for different environments
    if os.environ.get('VERCEL'):
        # Vercel-specific configuration
        app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///healthcare_bot.db')
        app.config['REDIS_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    else:
        # Render or other platform configuration
        app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost/healthcaredb')
        app.config['REDIS_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Common configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Twilio configuration
    app.config['TWILIO_ACCOUNT_SID'] = os.environ.get('TWILIO_ACCOUNT_SID')
    app.config['TWILIO_AUTH_TOKEN'] = os.environ.get('TWILIO_AUTH_TOKEN')
    app.config['TWILIO_PHONE_NUMBER'] = os.environ.get('TWILIO_PHONE_NUMBER')
    app.config['TWILIO_WHATSAPP_NUMBER'] = os.environ.get('TWILIO_WHATSAPP_NUMBER')
    
    # Google Cloud Translation API
    app.config['GOOGLE_TRANSLATE_API_KEY'] = os.environ.get('GOOGLE_TRANSLATE_API_KEY')
    
    # Government API endpoints
    app.config['MOHFW_API_URL'] = os.environ.get('MOHFW_API_URL', 'https://api.covid19india.org/data.json')
    app.config['COWIN_API_URL'] = os.environ.get('COWIN_API_URL', 'https://cdn-api.co-vin.in/api')
    
    # Initialize extensions
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    
    # Initialize Redis (with fallback for serverless)
    try:
        redis_client = redis.from_url(app.config['REDIS_URL'])
        redis_client.ping()
        app.redis = redis_client
    except:
        app.redis = None
        app.logger.warning("Redis not available, using in-memory storage")
    
    # Import and register blueprints
    from routes.api import api_bp
    from routes.webhook import webhook_bp
    from routes.main import main_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(webhook_bp, url_prefix='/webhook')
    app.register_blueprint(main_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {"error": "Not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {"status": "healthy", "message": "Healthcare Chatbot API is running"}
    
    return app

# Create the app instance
app = create_app()

# For Vercel, we need to expose the app as 'app'
# This is the entry point that Vercel will use
if __name__ == "__main__":
    app.run(debug=False)
