#!/usr/bin/env python3
import os
import sys
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from Chatbot import create_app
    app = create_app()
    print("✅ Enhanced healthcare chatbot initialized successfully!")
    print("🏥 Features enabled:")
    print("   • Enhanced chatbot with ML/NLP")
    print("   • Multilingual support (13+ languages)")
    print("   • WhatsApp/SMS integration ready")
    print("   • Government health data integration")
    print("   • Real-time alert system")
    print("   • Advanced healthcare models")
except ImportError as e:
    print(f"⚠️  Enhanced features not available: {e}")
    print("📋 Creating basic Flask app...")
    from Chatbot import app
    print("✅ Basic healthcare chatbot running")

try:
    from alert_system import alert_scheduler
    if not app.debug:
        alert_scheduler.start_scheduler()
        print("🚨 Alert scheduler started")
except ImportError:
    print("⚠️  Alert system not available")

@app.route('/health')
def health_check():
    """Health check endpoint for deployment"""
    return {
        'status': 'healthy',
        'version': '2.0.0',
        'features': 'enhanced' if 'enhanced_chatbot' in sys.modules else 'basic'
    }

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')

    print(f"🚀 Starting server on {host}:{port}")
    print(f"🔧 Debug mode: {debug_mode}")
    print(f"💻 Access at: http://localhost:{port}")

    if debug_mode:
        print("\n📱 Webhook URLs for Twilio setup:")
        print(f"   WhatsApp: http://localhost:{port}/webhook/whatsapp")
        print(f"   SMS: http://localhost:{port}/webhook/sms")

    app.run(host=host, port=port, debug=debug_mode)