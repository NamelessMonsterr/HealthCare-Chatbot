import os
from datetime import datetime
from threading import Thread
import time
from typing import List, Dict

try:
    from whatsapp_sms_handler import WhatsAppHandler, SMSHandler
    from health_data_service import health_data_service
    from translation_service import translation_service
    ENHANCED_FEATURES = True
except ImportError:
    ENHANCED_FEATURES = False
    print("⚠️  Enhanced features not available for alert system")

class SimpleAlertScheduler:
    """Simplified alert scheduler for health notifications"""

    def __init__(self):
        if ENHANCED_FEATURES:
            self.whatsapp_handler = WhatsAppHandler()
            self.sms_handler = SMSHandler()
            self.translation_service = translation_service
            print("✅ Alert scheduler initialized with messaging support")
        else:
            self.whatsapp_handler = None
            self.sms_handler = None
            self.translation_service = None
            print("⚠️  Alert scheduler initialized without messaging")

        self.subscribers: Dict[str, Dict] = {}  # phone->preferences
        self.alert_history: List[Dict] = []
        self.scheduler_running = False
        self.scheduler_thread = None

    def subscribe_user(self, phone_number: str, language: str = 'en', preferences: Dict = None):
        if not preferences:
            preferences = {
                'vaccination_reminders': True,
                'disease_outbreaks': True,
                'health_advisories': True
            }
        self.subscribers[phone_number] = {
            'language': language,
            'subscribed_at': datetime.now(),
            'preferences': preferences
        }
        print(f"✅ Subscribed {phone_number} to health alerts")
        return True

    def unsubscribe_user(self, phone_number: str):
        if phone_number in self.subscribers:
            del self.subscribers[phone_number]
            print(f"❌ Unsubscribed {phone_number} from health alerts")
        return True

    def send_vaccination_reminder(self, phone_number: str, vaccine_name: str, 
                                due_date: str, center_info: str = None):
        if not ENHANCED_FEATURES:
            print("⚠️  Cannot send alerts - messaging not configured")
            return False

        user_prefs = self.subscribers.get(phone_number, {})
        language = user_prefs.get('language', 'en')

        message = f"🏥 Vaccination Reminder\n\nYour {vaccine_name} is due on {due_date}."
        if center_info:
            message += f"\n\n📍 Center: {center_info}"

        message += "\n\nBook appointment via CoWIN app or visit the center.\nReply STOP to unsubscribe."

        if language != 'en' and self.translation_service:
            message = self.translation_service.translate_healthcare_response(message, language)

        results = {}
        if self.whatsapp_handler:
            results['whatsapp'] = self.whatsapp_handler.send_message(phone_number, message)
        if self.sms_handler:
            sms_message = f"VACCINATION: {vaccine_name} due {due_date}. Book via CoWIN. STOP to unsubscribe."
            results['sms'] = self.sms_handler.send_sms(phone_number, sms_message)

        self.alert_history.append({
            'type': 'vaccination_reminder',
            'phone': phone_number,
            'message': message,
            'sent_at': datetime.now(),
            'results': results
        })

        return results

    def send_health_advisory(self, advisory_title: str, advisory_message: str, 
                           urgency: str = "medium", target_users: List[str] = None):
        if not ENHANCED_FEATURES:
            print("⚠️  Cannot send alerts - messaging not configured")
            return False

        if not target_users:
            target_users = list(self.subscribers.keys())

        urgency_emojis = {
            "low": "ℹ️",
            "medium": "📢",
            "high": "⚠️",
            "critical": "🚨"
        }
        emoji = urgency_emojis.get(urgency, "📢")

        base_message = f"{emoji} Health Advisory: {advisory_title}\n\n{advisory_message}\n\nStay safe and follow health guidelines.\nReply STOP to unsubscribe."

        results = []

        for phone_number in target_users:
            if phone_number not in self.subscribers:
                continue

            user_prefs = self.subscribers[phone_number]
            if not user_prefs.get('preferences', {}).get('health_advisories', True):
                continue

            language = user_prefs.get('language', 'en')

            message = base_message
            if language != 'en' and self.translation_service:
                message = self.translation_service.translate_healthcare_response(message, language)

            user_results = {'phone': phone_number}
            if self.whatsapp_handler:
                user_results['whatsapp'] = self.whatsapp_handler.send_message(phone_number, message)
            if urgency in ['high', 'critical'] and self.sms_handler:
                sms_message = f"{urgency.upper()}: {advisory_title}. {advisory_message[:100]}... STOP to unsubscribe."
                user_results['sms'] = self.sms_handler.send_sms(phone_number, sms_message)

            results.append(user_results)

        self.alert_history.append({
            'type': 'health_advisory',
            'title': advisory_title,
            'urgency': urgency,
            'target_count': len(target_users),
            'sent_at': datetime.now(),
            'results': results
        })

        print(f"📢 Sent health advisory to {len(results)} users")
        return results

    def send_outbreak_alert(self, disease_name: str, location: str, 
                          prevention_measures: List[str], urgency: str = "high"):
        prevention_text = "\n".join([f"• {m}" for m in prevention_measures[:3]])

        message = f"🚨 Health Alert: {disease_name} Outbreak\n\n📍 Location: {location}\n\n🛡️ Prevention:\n{prevention_text}\n\nStay alert and follow health guidelines.\nSource: Health Department"

        target_users = [
            phone for phone, prefs in self.subscribers.items()
            if prefs.get('preferences', {}).get('disease_outbreaks', True)
        ]

        return self.send_health_advisory(f"{disease_name} Outbreak", message, urgency, target_users)

    def start_scheduler(self):
        if self.scheduler_running:
            print("⚠️  Scheduler already running")
            return

        self.scheduler_running = True
        self.scheduler_thread = Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        print("✅ Alert scheduler started")

    def stop_scheduler(self):
        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        print("🛑 Alert scheduler stopped")

    def _scheduler_loop(self):
        while self.scheduler_running:
            try:
                self._check_health_updates()
                for _ in range(360):  # Sleep 10 sec intervals to allow stop
                    if not self.scheduler_running:
                        break
                    time.sleep(10)
            except Exception as e:
                print(f"❌ Scheduler error: {e}")
                time.sleep(60)

    def _check_health_updates(self):
        if not ENHANCED_FEATURES:
            return
        try:
            advisories = health_data_service.get_health_advisories()
            if advisories and 'advisories' in advisories:
                for advisory in advisories['advisories']:
                    advisory_id = advisory.get('id', '')
                    already_sent = any(alert.get('advisory_id') == advisory_id for alert in self.alert_history)
                    if not already_sent and advisory.get('severity') in ['high', 'critical']:
                        self.send_health_advisory(
                            advisory.get('title', 'Health Update'),
                            advisory.get('description', ''),
                            advisory.get('severity', 'medium')
                        )
                        if self.alert_history:
                            self.alert_history[-1]['advisory_id'] = advisory_id
        except Exception as e:
            print(f"❌ Health update check error: {e}")

    def get_statistics(self) -> Dict:
        return {
            'total_subscribers': len(self.subscribers),
            'alerts_sent_today': len([
                alert for alert in self.alert_history
                if alert['sent_at'].date() == datetime.now().date()
            ]),
            'total_alerts_sent': len(self.alert_history),
            'scheduler_running': self.scheduler_running,
            'last_check': self.alert_history[-1]['sent_at'].isoformat() if self.alert_history else None
        }

    def get_subscribers_list(self) -> List[Dict]:
        return [
            {
                'phone': phone,
                'language': prefs.get('language', 'en'),
                'subscribed_at': prefs.get('subscribed_at', datetime.now()).isoformat(),
                'preferences': prefs.get('preferences', {})
            }
            for phone, prefs in self.subscribers.items()
        ]

# Global instance
alert_scheduler = SimpleAlertScheduler()

if __name__ == "__main__":
    print("🔧 Testing Alert System...")

    test_phone = "+919876543210"
    alert_scheduler.subscribe_user(test_phone, 'hi', {
        'vaccination_reminders': True,
        'disease_outbreaks': True,
        'health_advisories': True
    })
    print(f"   Subscribers: {len(alert_scheduler.subscribers)}")

    if ENHANCED_FEATURES:
        print("   Testing vaccination reminder...")
        alert_scheduler.send_vaccination_reminder(test_phone, "COVID-19 Booster", "2024-01-15", "Primary Health Center, Local Area")

        print("   Testing health advisory...")
        alert_scheduler.send_health_advisory("Winter Health Tips", "Keep warm, stay hydrated, and get flu vaccination.", "low", [test_phone])

    stats = alert_scheduler.get_statistics()
    print(f"   Statistics: {stats}")
    print("✅ Alert system test completed")