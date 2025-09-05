import os
import logging
from datetime import datetime

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("⚠️  Twilio not installed. WhatsApp/SMS features disabled.")

class WhatsAppHandler:
    """Handle WhatsApp messages via Twilio"""

    def __init__(self):
        if TWILIO_AVAILABLE:
            self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
            self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
            self.whatsapp_number = os.environ.get('WHATSAPP_NUMBER')

            if self.account_sid and self.auth_token:
                try:
                    self.client = Client(self.account_sid, self.auth_token)
                    print("✅ WhatsApp handler initialized")
                except Exception as e:
                    print(f"⚠️  WhatsApp initialization error: {e}")
                    self.client = None
            else:
                print("⚠️  WhatsApp credentials not configured")
                self.client = None
        else:
            self.client = None

    def send_message(self, to_number, message, media_url=None):
        """Send WhatsApp message to user"""
        if not self.client:
            return {"error": "WhatsApp not configured"}

        try:
            # Format phone number for WhatsApp
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'

            from_number = f'whatsapp:{self.whatsapp_number}'

            message_kwargs = {
                'body': message,
                'from_': from_number,
                'to': to_number
            }

            if media_url:
                message_kwargs['media_url'] = [media_url]

            message_obj = self.client.messages.create(**message_kwargs)

            print(f"✅ WhatsApp sent to {to_number}: {message_obj.sid}")

            return {
                "success": True,
                "message_sid": message_obj.sid,
                "status": message_obj.status
            }

        except Exception as e:
            error_msg = f"WhatsApp send error: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}

    def send_healthcare_alert(self, to_number, alert_type, message, urgency="normal"):
        urgency_emojis = {
            "low": "ℹ️",
            "normal": "📢", 
            "high": "⚠️",
            "critical": "🚨"
        }

        emoji = urgency_emojis.get(urgency, "📢")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        formatted_message = f"""{emoji} *Healthcare Alert: {alert_type.title()}*\n\n{message}\n\n_Sent at {timestamp}_\n_Reply STOP to unsubscribe_"""

        return self.send_message(to_number, formatted_message)

    def send_vaccination_reminder(self, to_number, user_name, vaccine_name, due_date, center_info=None):
        message = f"""🏥 *Vaccination Reminder*\n\nHello {user_name},\n\nYour {vaccine_name} vaccination is due on {due_date}."""

        if center_info:
            message += f"""\n\n📍 *Vaccination Center:*\n{center_info}"""

        message += """\n\nPlease visit the center or book an appointment through CoWIN portal.\n\nReply 'STOP REMINDERS' to unsubscribe from vaccination alerts."""

        return self.send_message(to_number, message)

    def send_symptom_guidance(self, to_number, symptoms, recommendations, doctor_contact=None):
        message = f"""🩺 *Health Consultation*\n\n*Reported Symptoms:* {symptoms}\n\n*Recommendations:*\n{recommendations}"""

        if doctor_contact:
            message += f"""\n\n🏥 *Consult Doctor:*\n{doctor_contact}"""

        message += """\n\n⚠️ *Disclaimer:* This is AI-generated guidance. Please consult a qualified healthcare professional for proper diagnosis."""

        return self.send_message(to_number, message)

class SMSHandler:
    """Handle SMS messages via Twilio"""

    def __init__(self):
        if TWILIO_AVAILABLE:
            self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
            self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
            self.phone_number = os.environ.get('TWILIO_PHONE_NUMBER')

            if self.account_sid and self.auth_token:
                try:
                    self.client = Client(self.account_sid, self.auth_token)
                    print("✅ SMS handler initialized")
                except Exception as e:
                    print(f"⚠️  SMS initialization error: {e}")
                    self.client = None
            else:
                print("⚠️  SMS credentials not configured")
                self.client = None
        else:
            self.client = None

    def send_sms(self, to_number, message):
        """Send SMS message to user"""
        if not self.client:
            return {"error": "SMS not configured"}

        try:
            # Ensure SMS length limit
            if len(message) > 160:
                message = message[:157] + "..."
            
            message_obj = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_number
            )

            print(f"✅ SMS sent to {to_number}: {message_obj.sid}")

            return {
                "success": True,
                "message_sid": message_obj.sid,
                "status": message_obj.status
            }

        except Exception as e:
            error_msg = f"SMS send error: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}

    def send_health_alert_sms(self, to_number, alert_message):
        """Send health alert via SMS with character limit optimization"""
        if len(alert_message) > 160:
            alert_message = alert_message[:157] + "..."
        return self.send_sms(to_number, alert_message)

    def send_vaccination_sms(self, to_number, vaccine_name, due_date):
        message = f"HEALTH ALERT: Your {vaccine_name} vaccination is due on {due_date}. Book appointment via CoWIN. Reply STOP to unsubscribe."
        return self.send_sms(to_number, message)

# Test functions for setup
def test_whatsapp_setup():
    handler = WhatsAppHandler()
    if handler.client:
        print("✅ WhatsApp setup is working!")
        return True
    else:
        print("❌ WhatsApp setup needs configuration")
        print("   1. Sign up at twilio.com")
        print("   2. Get WhatsApp Business API access")
        print("   3. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, WHATSAPP_NUMBER in .env")
        return False

def test_sms_setup():
    handler = SMSHandler()
    if handler.client:
        print("✅ SMS setup is working!")
        return True
    else:
        print("❌ SMS setup needs configuration")
        print("   1. Sign up at twilio.com")
        print("   2. Buy a phone number")
        print("   3. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER in .env")
        return False

if __name__ == "__main__":
    print("🔧 Testing Twilio Setup...")
    whatsapp_ok = test_whatsapp_setup()
    sms_ok = test_sms_setup()

    if whatsapp_ok and sms_ok:
        print("🎉 All messaging services configured correctly!")
    else:
        print("⚠️  Some services need configuration. Check .env file.")