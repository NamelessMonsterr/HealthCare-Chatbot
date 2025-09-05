import os
import json
import random
from datetime import datetime
from typing import Dict, Tuple

# Try to import advanced ML libraries, else fallback
try:
    import nltk
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    ADVANCED_ML_AVAILABLE = True
except ImportError:
    ADVANCED_ML_AVAILABLE = False
    print("⚠️  Advanced ML libraries not available. Falling back to basic mode.")

class EnhancedChatBot:
    """Enhanced healthcare chatbot with improved NLP"""

    def __init__(self):
        self.intents_data = self.load_enhanced_intents()

        if ADVANCED_ML_AVAILABLE:
            self.tfidf_vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
            self.training_patterns = []
            self.training_labels = []
            self._train_classifier()

        self.user_sessions = {}
        print("✅ Enhanced chatbot initialized")

    def load_enhanced_intents(self) -> Dict:
        enhanced_intents = {
            "intents": [
                {
                    "tag": "greeting",
                    "patterns": [
                        "Hi", "Hello", "Good morning", "Good afternoon", "Good evening",
                        "Hey there", "Namaste", "Salaam", "Vanakkam", "Adaab", "Sat sri akal"
                    ],
                    "responses": [
                        "🏥 Hello! I'm your healthcare assistant. How can I help you today?",
                        "👋 Hi there! I'm here to provide health information and support. What can I assist you with?",
                        "🩺 Welcome to the healthcare chatbot! Feel free to ask about symptoms, medications, or health advice."
                    ]
                },
                {
                    "tag": "emergency",
                    "patterns": [
                        "emergency", "urgent", "help me", "chest pain", "heart attack", 
                        "difficulty breathing", "severe pain", "bleeding heavily", "unconscious",
                        "emergency ambulance", "call doctor", "intensive pain", "can't breathe"
                    ],
                    "responses": [
                        "🚨 **MEDICAL EMERGENCY** - Please call emergency services immediately:\n\n🚑 India: **108** (Ambulance)\n🏥 Or visit nearest hospital\n\n⚠️ This is not a substitute for immediate medical care!"
                    ]
                },
                {
                    "tag": "covid_symptoms",
                    "patterns": [
                        "covid symptoms", "coronavirus", "covid-19", "fever cough",
                        "loss of taste", "loss of smell", "covid test", "quarantine",
                        "covid vaccination", "omicron", "delta variant"
                    ],
                    "responses": [
                        "🦠 **COVID-19 Common Symptoms:**\n• Fever (above 100.4°F)\n• Dry cough\n• Fatigue\n• Loss of taste/smell\n• Difficulty breathing\n• Body aches\n\n**If you have symptoms:**\n1️⃣ Get tested immediately\n2️⃣ Isolate yourself\n3️⃣ Consult a doctor\n4️⃣ Monitor oxygen levels"
                    ]
                },
                {
                    "tag": "fever",
                    "patterns": [
                        "I have fever", "fever", "high temperature", "body heat", "bukhar", 
                        "I feel hot", "temperature", "chills", "sweating"
                    ],
                    "responses": [
                        "🌡️ **Fever Management:**\n\n**Immediate Care:**\n• Rest and stay hydrated\n• Take paracetamol as directed\n• Use cool cloth on forehead\n• Monitor temperature regularly\n\n⚠️ **Seek medical help if:**\n• Fever above 103°F (39.4°C)\n• Persistent for more than 3 days\n• Accompanied by severe symptoms"
                    ]
                },
                {
                    "tag": "cough",
                    "patterns": [
                        "I have cough", "coughing", "dry cough", "wet cough", "khansi",
                        "throat irritation", "persistent cough", "chest congestion"
                    ],
                    "responses": [
                        "😷 **Cough Relief:**\n\n**Home Remedies:**\n• Warm water with honey and lemon\n• Steam inhalation\n• Stay hydrated\n• Avoid cold drinks\n• Use humidifier\n\n⚠️ **See doctor if:**\n• Cough persists >2 weeks\n• Blood in cough\n• High fever with cough\n• Difficulty breathing"
                    ]
                },
                {
                    "tag": "headache",
                    "patterns": [
                        "headache", "head pain", "migraine", "sir dard", "head ache",
                        "severe headache", "head hurts", "brain pain"
                    ],
                    "responses": [
                        "🤕 **Headache Relief:**\n\n**Quick Relief:**\n• Rest in dark, quiet room\n• Apply cold/warm compress\n• Stay hydrated\n• Gentle head massage\n• Paracetamol if needed\n\n🚨 **Emergency signs:**\n• Sudden severe headache\n• Headache with fever & stiff neck\n• Vision changes\n• Confusion or weakness"
                    ]
                },
                {
                    "tag": "vaccination_schedule",
                    "patterns": [
                        "vaccination schedule", "vaccine calendar", "immunization", 
                        "child vaccination", "adult vaccines", "booster dose",
                        "vaccine due", "vaccination chart", "tika", "vaccine list"
                    ],
                    "responses": [
                        "💉 **Vaccination Schedule:**\n\n👶 **For Children:**\n• Birth: BCG, OPV, Hep-B\n• 6 weeks: DTwP, IPV, Hib, Rotavirus, PCV\n• 10 weeks: DTwP, IPV, Hib, Rotavirus, PCV\n• 14 weeks: DTwP, IPV, Hib, Rotavirus, PCV\n\n🧑 **For Adults:**\n• COVID-19: As per guidelines\n• Annual flu vaccine\n• Tetanus booster every 10 years\n\n📱 Use CoWIN app for COVID vaccination booking!"
                    ]
                },
                {
                    "tag": "find_doctor",
                    "patterns": [
                        "find doctor", "doctor near me", "hospital nearby", "specialist",
                        "cardiologist", "dermatologist", "pediatrician", "gynecologist",
                        "orthopedic", "ENT doctor", "eye doctor", "dentist", "daktar"
                    ],
                    "responses": [
                        "🏥 **Find Healthcare Providers:**\n\n**Government Hospitals:**\n• Visit: mohfw.gov.in\n• Call: 104 (Health Helpline)\n• Ayushman Bharat beneficiaries\n\n**Online Directories:**\n• Practo.com\n• 1mg.com\n• Apollo hospitals\n• Local government health portals\n\n📍 **Need specific recommendations?**\nPlease share your location (city/state) for targeted suggestions."
                    ]
                },
                # ... More intents can be added similarly ...
            ]
        }
        return enhanced_intents

    def _train_classifier(self):
        if not ADVANCED_ML_AVAILABLE:
            return
        
        patterns = []
        labels = []
        
        for intent in self.intents_data["intents"]:
            for pattern in intent["patterns"]:
                patterns.append(pattern.lower())
                labels.append(intent["tag"])
        
        try:
            self.training_vectors = self.tfidf_vectorizer.fit_transform(patterns)
            self.training_patterns = patterns
            self.training_labels = labels
            print(f"✅ Trained on {len(patterns)} patterns")
        except Exception as e:
            print(f"⚠️  Training error: {e}")

    def predict_intent(self, user_input: str) -> Tuple[str, float]:
        if ADVANCED_ML_AVAILABLE and hasattr(self, 'training_vectors'):
            try:
                user_vector = self.tfidf_vectorizer.transform([user_input.lower()])
                similarities = cosine_similarity(user_vector, self.training_vectors).flatten()
                
                if len(similarities) > 0:
                    best_match_idx = np.argmax(similarities)
                    confidence = similarities[best_match_idx]
                    predicted_intent = self.training_labels[best_match_idx]
                    return predicted_intent, confidence
            except Exception as e:
                print(f"⚠️  ML prediction error: {e}")
        
        return self._fallback_intent_prediction(user_input)

    def _fallback_intent_prediction(self, user_input: str) -> Tuple[str, float]:
        user_input_lower = user_input.lower()
        if any(word in user_input_lower for word in ["emergency", "urgent", "chest pain", "heart attack", "can't breathe", "unconscious"]):
            return "emergency", 0.9
        elif any(word in user_input_lower for word in ["covid", "coronavirus", "covid-19", "omicron", "loss of taste", "loss of smell"]):
            return "covid_symptoms", 0.8
        elif any(word in user_input_lower for word in ["fever", "temperature", "high temp", "bukhar"]):
            return "fever", 0.8
        elif any(word in user_input_lower for word in ["cough", "khansi", "coughing"]):
            return "cough", 0.8
        elif any(word in user_input_lower for word in ["headache", "sir dard", "migraine", "head pain"]):
            return "headache", 0.8
        elif any(word in user_input_lower for word in ["doctor", "hospital", "specialist", "daktar"]):
            return "find_doctor", 0.8
        elif any(word in user_input_lower for word in ["vaccine", "vaccination", "tika", "immunization"]):
            return "vaccination_schedule", 0.8
        elif any(word in user_input_lower for word in ["medicine", "medication", "dawa", "tablet"]):
            return "medicine_info", 0.7
        elif any(word in user_input_lower for word in ["depression", "anxiety", "stress", "sad", "worried"]):
            return "mental_health", 0.8
        elif any(word in user_input_lower for word in ["first aid", "bleeding", "burn", "wound", "accident"]):
            return "first_aid", 0.7
        elif any(word in user_input_lower for word in ["hi", "hello", "namaste", "hey"]):
            return "greeting", 0.9
        else:
            return "general_health", 0.5

    def get_response(self, user_input: str, user_phone: str=None, user_name: str="User", language: str="en") -> str:
        if user_phone:
            if user_phone not in self.user_sessions:
                self.user_sessions[user_phone] = {
                    "conversation_history": [],
                    "user_name": user_name,
                    "language": language,
                    "session_start": datetime.now()
                }
            session = self.user_sessions[user_phone]
            session["conversation_history"].append({
                "user_input": user_input,
                "timestamp": datetime.now()
            })

        predicted_intent, confidence = self.predict_intent(user_input)
        response = self._get_intent_response(predicted_intent)

        if user_name != "User":
            response = f"Hello {user_name}! {response}"

        if predicted_intent != "emergency" and self._contains_emergency_keywords(user_input):
            response += "\n\n⚠️ **If this is a medical emergency, please call 108 immediately!**"

        follow_up = self._get_follow_up_suggestions(predicted_intent)
        if follow_up:
            response += f"\n\n**You might also want to:**\n{follow_up}"

        return response

    def get_sms_response(self, user_input: str, user_phone: str=None) -> str:
        predicted_intent, _ = self.predict_intent(user_input)
        sms_responses = {
            "emergency": "🚨 EMERGENCY: Call 108 now! Visit nearest hospital immediately.",
            "fever": "🌡️ FEVER: Rest, hydrate, paracetamol. See doctor if >103°F or persists >3 days.",
            "cough": "😷 COUGH: Honey+warm water, steam. See doctor if >2 weeks or blood.",
            "covid_symptoms": "🦠 COVID: Get tested, isolate, consult doctor. Monitor oxygen levels.",
            "headache": "🤕 HEADACHE: Rest in dark room, hydrate, cold compress. Emergency if sudden/severe.",
            "find_doctor": "🏥 DOCTORS: Call 104 helpline or visit mohfw.gov.in, Practo.com",
            "vaccination_schedule": "💉 VACCINES: Use CoWIN app or visit nearest PHC. Call 104 for info.",
            "mental_health": "🧠 MENTAL HEALTH: Call 1800-599-0019 or iCall 9152987821 for help.",
            "first_aid": "🚑 FIRST AID: Clean wounds, apply pressure for bleeding. Call 108 if severe.",
            "medicine_info": "💊 MEDICINES: Consult doctor/pharmacist. Never self-medicate.",
            "greeting": "🏥 Health Bot: Ask symptoms, find doctors, vaccine info. Type HELP for commands."
        }
        return sms_responses.get(predicted_intent, "Health query received. For detailed help, use web or WhatsApp.")

    def _get_intent_response(self, intent: str) -> str:
        for intent_data in self.intents_data["intents"]:
            if intent_data["tag"] == intent:
                return random.choice(intent_data["responses"])
        return ("I understand you have a health-related question. "
                "Could you provide more specific information about your symptoms or concern? "
                "I'm here to help with health guidance, but please consult a healthcare "
                "professional for proper diagnosis and treatment.")

    def _contains_emergency_keywords(self, text: str) -> bool:
        emergency_keywords = [
            "chest pain", "heart attack", "difficulty breathing", "can't breathe",
            "severe bleeding", "unconscious", "choking", "severe burn"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in emergency_keywords)

    def _get_follow_up_suggestions(self, intent: str) -> str:
        suggestions = {
            "fever": "• Monitor temperature regularly\n• Stay hydrated with fluids\n• Rest and avoid exertion",
            "cough": "• Avoid smoking and pollutants\n• Use humidifier\n• Sleep with head elevated",
            "find_doctor": "• Check doctor credentials\n• Read patient reviews\n• Verify insurance coverage",
            "vaccination_schedule": "• Set vaccination reminders\n• Keep vaccination records\n• Ask about side effects",
            "mental_health": "• Practice daily meditation\n• Exercise regularly\n• Connect with support groups"
        }
        return suggestions.get(intent, "")

# Global instance
enhanced_chatbot = EnhancedChatBot()