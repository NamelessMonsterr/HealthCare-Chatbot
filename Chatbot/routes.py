import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from Chatbot import app, db, bcrypt, mail
from Chatbot.forms import (RegistrationForm, LoginForm)
from Chatbot.models import User
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from datetime import datetime
import json

# Import enhanced services
try:
    from enhanced_chatbot import enhanced_chatbot
    from translation_service import translation_service
    from whatsapp_sms_handler import WhatsAppHandler, SMSHandler
    from health_data_service import health_data_service
    ENHANCED_FEATURES = True
except ImportError:
    # Fallback to original main.py
    import main
    ENHANCED_FEATURES = False

# Initialize handlers if available
if ENHANCED_FEATURES:
    whatsapp_handler = WhatsAppHandler()
    sms_handler = SMSHandler()

arr = [0]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/chatbot', methods=['GET'])
@login_required
def bot():
    length = len(arr)
    message = request.args.get('msg')
    if message is not None:
        arr.append(message)
        arr.append(1)
        # Use enhanced chatbot if available
        if ENHANCED_FEATURES:
            user_phone = getattr(current_user, 'phone_number', None)
            response = enhanced_chatbot.get_response(
                message, 
                user_phone=user_phone,
                user_name=current_user.username,
                language='en'
            )
        else:
            # Fallback to original chatbot
            response = main.callthis(message)
        arr.append(response)
        arr.append(0)
        length = len(arr)
        print(arr)
    return render_template('bot.html', arr=arr, length=length)

# API endpoints for health data and translation (for web clients or integrations)
@app.route('/api/health-data/covid-stats')
def get_covid_stats():
    if not ENHANCED_FEATURES:
        return jsonify({'error': 'Enhanced features not available'}), 501
    state = request.args.get('state')
    district = request.args.get('district')
    try:
        data = health_data_service.get_covid_statistics(state, district)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health-data/vaccination-centers')
def get_vaccination_centers():
    if not ENHANCED_FEATURES:
        return jsonify({'error': 'Enhanced features not available'}), 501
    pincode = request.args.get('pincode')
    date = request.args.get('date')
    if not pincode:
        return jsonify({'error': 'Pincode is required'}), 400
    try:
        data = health_data_service.get_vaccination_centers(pincode, date)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/translate', methods=['POST'])
def translate_text():
    if not ENHANCED_FEATURES:
        return jsonify({'error': 'Enhanced features not available'}), 501
    data = request.json
    text = data.get('text', '')
    target_language = data.get('target_language', 'en')
    if not text:
        return jsonify({'error': 'Text is required'}), 400
    try:
        translated = translation_service.translate_text(text, target_language)
        return jsonify({
            'original_text': text,
            'translated_text': translated,
            'target_language': target_language
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/languages')
def get_supported_languages():
    if not ENHANCED_FEATURES:
        return jsonify({'error': 'Enhanced features not available'}), 501
    try:
        languages_info = translation_service.get_supported_languages_info()
        return jsonify(languages_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/enhanced', methods=['POST'])
def enhanced_chat():
    if not ENHANCED_FEATURES:
        return jsonify({'error': 'Enhanced features not available'}), 501
    data = request.json
    message = data.get('message', '')
    language = data.get('language', 'en')
    user_phone = data.get('user_phone')
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    try:
        user_name = current_user.username if current_user.is_authenticated else 'User'
        response = enhanced_chatbot.get_response(
            message, 
            user_phone=user_phone,
            user_name=user_name,
            language=language
        )
        # Translate response if needed
        if language != 'en':
            response = translation_service.translate_healthcare_response(
                response, language, message)
        return jsonify({
            'response': response,
            'language': language,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WhatsApp webhook
@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    if not ENHANCED_FEATURES:
        return 'Enhanced features not available', 501
    try:
        from twilio.twiml.messaging_response import MessagingResponse
        incoming_msg = request.values.get('Body', '').strip()
        sender_number = request.values.get('From', '')
        sender_name = request.values.get('ProfileName', 'User')
        if sender_number.startswith('whatsapp:'):
            sender_number = sender_number.replace('whatsapp:', '')
        resp = MessagingResponse()
        if incoming_msg.upper() == 'HELP':
            help_text = '''🏥 Healthcare Chatbot Commands:

💬 Ask about symptoms
📋 Vaccination schedules  
🏥 Find nearby hospitals
💊 Medicine information
🌍 Languages: Send 'hi', 'te', 'ta' etc.
❓ Help: Type HELP

Example: "I have fever and cough"'''
            resp.message(help_text)
            return str(resp)
        detected_lang = translation_service.detect_language(incoming_msg)
        chatbot_response = enhanced_chatbot.get_response(
            incoming_msg, 
            user_phone=sender_number,
            user_name=sender_name,
            language=detected_lang
        )
        if detected_lang and detected_lang != 'en':
            chatbot_response = translation_service.translate_healthcare_response(
                chatbot_response, detected_lang, incoming_msg)
        resp.message(chatbot_response)
        return str(resp)
    except Exception as e:
        app.logger.error(f"WhatsApp webhook error: {str(e)}")
        resp = MessagingResponse()
        resp.message("Sorry, I'm experiencing technical difficulties. Please try again later.")
        return str(resp)

# SMS webhook
@app.route('/webhook/sms', methods=['POST'])
def sms_webhook():
    if not ENHANCED_FEATURES:
        return 'Enhanced features not available', 501
    try:
        from twilio.twiml.messaging_response import MessagingResponse
        incoming_msg = request.values.get('Body', '').strip()
        sender_number = request.values.get('From', '')
        resp = MessagingResponse()
        if incoming_msg.upper() == 'HELP':
            resp.message("Health Bot: Ask symptoms, vaccination info, or hospitals. Text STOP to unsubscribe.")
            return str(resp)
        sms_response = enhanced_chatbot.get_sms_response(incoming_msg, sender_number)
        resp.message(sms_response)
        return str(resp)
    except Exception as e:
        app.logger.error(f"SMS webhook error: {str(e)}")
        resp = MessagingResponse()
        resp.message("Error processing request. Try again later.")
        return str(resp)

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'enhanced_features': ENHANCED_FEATURES,
        'version': '2.0.0'
    })

# Password reset routes omitted for brevity