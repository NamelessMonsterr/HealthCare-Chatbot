from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from Chatbot import db, login_manager, app
from flask_login import UserMixin
import json

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """Enhanced user model with healthcare fields"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=True)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    
    # Enhanced healthcare fields
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    blood_group = db.Column(db.String(5), nullable=True)
    emergency_contact = db.Column(db.String(15), nullable=True)
    
    # Location information
    state = db.Column(db.String(50), nullable=True)
    district = db.Column(db.String(50), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    
    # Preferences
    preferred_language = db.Column(db.String(5), default='en')
    is_subscribed_alerts = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    medical_records = db.relationship('MedicalRecord', backref='patient', lazy=True, cascade='all, delete-orphan')
    vaccination_records = db.relationship('VaccinationRecord', backref='patient', lazy=True)
    chat_sessions = db.relationship('ChatSession', backref='user', lazy=True)
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
    
    def get_age(self):
        """Calculate user's age"""
        if self.date_of_birth:
            today = datetime.now().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.phone_number}')"

class MedicalRecord(db.Model):
    """Store user's medical history and records"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    record_type = db.Column(db.String(50), nullable=False)  # consultation, prescription, test_result
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Medical details (stored as JSON strings for SQLite compatibility)
    symptoms = db.Column(db.Text, nullable=True)  # JSON string of symptoms
    diagnosis = db.Column(db.String(500), nullable=True)
    prescribed_medicines = db.Column(db.Text, nullable=True)  # JSON string
    doctor_name = db.Column(db.String(100), nullable=True)
    hospital_name = db.Column(db.String(200), nullable=True)
    
    # Dates
    record_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_symptoms_list(self):
        """Get symptoms as Python list"""
        if self.symptoms:
            try:
                return json.loads(self.symptoms)
            except:
                return []
        return []
    
    def set_symptoms_list(self, symptoms_list):
        """Set symptoms from Python list"""
        self.symptoms = json.dumps(symptoms_list)
    
    def __repr__(self):
        return f"MedicalRecord('{self.title}', '{self.record_date}')"

class VaccinationRecord(db.Model):
    """Track user vaccination history and schedules"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    vaccine_name = db.Column(db.String(100), nullable=False)
    vaccine_type = db.Column(db.String(50), nullable=True)  # COVID, Flu, etc.
    dose_number = db.Column(db.Integer, nullable=False, default=1)
    
    # Scheduling
    due_date = db.Column(db.Date, nullable=True)
    administered_date = db.Column(db.Date, nullable=True)
    next_due_date = db.Column(db.Date, nullable=True)
    
    # Location and provider
    vaccination_center = db.Column(db.String(200), nullable=True)
    administered_by = db.Column(db.String(100), nullable=True)
    batch_number = db.Column(db.String(50), nullable=True)
    
    # Status
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, missed
    reminder_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_due(self):
        """Check if vaccination is due"""
        if self.due_date and self.status == 'scheduled':
            return datetime.now().date() >= self.due_date
        return False
    
    def __repr__(self):
        return f"VaccinationRecord('{self.vaccine_name}', '{self.due_date}')"

class ChatSession(db.Model):
    """Store chat conversations for analysis"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    phone_number = db.Column(db.String(15), nullable=True)  # For WhatsApp/SMS users
    
    session_id = db.Column(db.String(100), nullable=False, unique=True)
    channel = db.Column(db.String(20), nullable=False)  # web, whatsapp, sms
    
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    language = db.Column(db.String(5), default='en')
    
    messages = db.Column(db.Text, default='[]')  # JSON string
    
    identified_symptoms = db.Column(db.Text, nullable=True)  # JSON string
    predicted_conditions = db.Column(db.Text, nullable=True)  # JSON string
    urgency_level = db.Column(db.String(10), nullable=True)
    
    user_satisfaction = db.Column(db.Integer, nullable=True)  # 1-5 rating
    feedback_text = db.Column(db.Text, nullable=True)
    
    def add_message(self, sender, message, intent=None, confidence=None):
        message_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'sender': sender,  # 'user' or 'bot'
            'message': message,
            'intent': intent,
            'confidence': confidence
        }
        try:
            messages_list = json.loads(self.messages) if self.messages else []
        except:
            messages_list = []
        messages_list.append(message_data)
        self.messages = json.dumps(messages_list)
    
    def get_messages_list(self):
        try:
            return json.loads(self.messages) if self.messages else []
        except:
            return []
    
    def __repr__(self):
        return f"ChatSession('{self.session_id}', '{self.channel}')"

class HealthAlert(db.Model):
    """Store health alerts and notifications"""
    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.String(100), unique=True, nullable=False)
    
    alert_type = db.Column(db.String(30), nullable=False)  # vaccination_reminder, disease_outbreak
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    urgency = db.Column(db.String(10), nullable=False)  # low, medium, high, critical
    
    target_location = db.Column(db.String(100), nullable=True)
    target_age_group = db.Column(db.String(20), nullable=True)
    
    scheduled_time = db.Column(db.DateTime, nullable=True)
    sent_time = db.Column(db.DateTime, nullable=True)
    expiry_time = db.Column(db.DateTime, nullable=True)
    
    target_user_count = db.Column(db.Integer, default=0)
    sent_count = db.Column(db.Integer, default=0)
    delivered_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    
    status = db.Column(db.String(20), default='pending')  # pending, sent, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"HealthAlert('{self.alert_id}', '{self.title}')"

class SystemMetrics(db.Model):
    """Track system performance and usage metrics"""
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(50), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    metric_unit = db.Column(db.String(20), nullable=True)
    
    category = db.Column(db.String(30), nullable=False)  # performance, usage, health
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def record_metric(name, value, category, unit=None):
        metric = SystemMetrics(
            metric_name=name,
            metric_value=value,
            metric_unit=unit,
            category=category
        )
        db.session.add(metric)
        db.session.commit()
        return metric
    
    def __repr__(self):
        return f"SystemMetrics('{self.metric_name}': {self.metric_value})"

# Initialize DB tables on startup
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database initialization error: {e}")