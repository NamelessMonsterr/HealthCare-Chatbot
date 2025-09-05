import os
import logging
from typing import Optional, Dict

try:
    from langdetect import detect, DetectorFactory
    from langdetect.lang_detect_exception import LangDetectException
    LANGDETECT_AVAILABLE = True
    DetectorFactory.seed = 0  # for consistent detection
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("⚠️  langdetect not available. Language detection disabled.")

try:
    from google.cloud import translate_v2 as translate
    GOOGLE_TRANSLATE_AVAILABLE = True
except ImportError:
    GOOGLE_TRANSLATE_AVAILABLE = False
    print("⚠️  Google Cloud Translation not available. Using local fallback.")

class TranslationService:
    """Enhanced translation service supporting multiple Indian languages"""

    SUPPORTED_LANGUAGES = {
        'en': {'name': 'English', 'native': 'English'},
        'hi': {'name': 'Hindi', 'native': 'हिन्दी'},
        'bn': {'name': 'Bengali', 'native': 'বাংলা'},
        'te': {'name': 'Telugu', 'native': 'తెలుగు'},
        'ta': {'name': 'Tamil', 'native': 'தமிழ்'},
        'gu': {'name': 'Gujarati', 'native': 'ગુજરાતી'},
        'kn': {'name': 'Kannada', 'native': 'ಕನ್ನಡ'},
        'ml': {'name': 'Malayalam', 'native': 'മലയാളം'},
        'mr': {'name': 'Marathi', 'native': 'मराठी'},
        'pa': {'name': 'Punjabi', 'native': 'ਪੰਜਾਬੀ'},
        'or': {'name': 'Odia', 'native': 'ଓଡ଼ିଆ'},
        'as': {'name': 'Assamese', 'native': 'অসমীয়া'},
        'ur': {'name': 'Urdu', 'native': 'اردو'}
    }

    HEALTHCARE_TRANSLATIONS = {
        # Example translation dictionary for healthcare terms
        'fever': {
            'hi': 'बुखार', 'bn': 'জ্বর', 'te': 'జ్వరం', 'ta': 'காய்ச்சல்',
            'gu': 'તાવ', 'kn': 'ಜ್ವರ', 'ml': 'പനി', 'mr': 'ताप',
            'pa': 'ਬੁਖ਼ਾਰ', 'or': 'ଜ୍ୱର', 'ur': 'بخار'
        }
        # Add other key healthcare translations as needed
    }

    def __init__(self):
        self.google_client = None
        if GOOGLE_TRANSLATE_AVAILABLE and os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
            try:
                self.google_client = translate.Client()
                print("✅ Google Translate initialized")
            except Exception as e:
                print(f"⚠️  Google Translate initialization failed: {e}")

        print(f"✅ Translation service initialized for {len(self.SUPPORTED_LANGUAGES)} languages")

    def detect_language(self, text: str) -> Optional[str]:
        if not text or len(text.strip()) < 3:
            return 'en'  # Default to English for short texts

        if LANGDETECT_AVAILABLE:
            try:
                detected = detect(text)
                if detected in self.SUPPORTED_LANGUAGES:
                    return detected
                else:
                    return 'en'
            except LangDetectException:
                pass

        if self.google_client:
            try:
                result = self.google_client.detect_language(text)
                detected = result['language']
                if detected in self.SUPPORTED_LANGUAGES:
                    return detected
            except Exception as e:
                logging.error(f"Google Translate detection error: {e}")

        return 'en'

    def translate_text(self, text: str, target_language: str = 'en', source_language: str = None) -> str:
        if not text or target_language == 'en':
            return text

        if target_language not in self.SUPPORTED_LANGUAGES:
            print(f"⚠️  Unsupported language: {target_language}")
            return text

        if self.google_client:
            try:
                result = self.google_client.translate(
                    text,
                    target_language=target_language,
                    source_language=source_language
                )
                return result['translatedText']
            except Exception as e:
                print(f"⚠️  Google Translate error: {e}")

        # Fallback: simple dictionary-based translation (for demonstration)
        for eng_term, translations in self.HEALTHCARE_TRANSLATIONS.items():
            if eng_term in text.lower():
                translated_term = translations.get(target_language, eng_term)
                text = text.lower().replace(eng_term, translated_term)
        return text

    def translate_healthcare_response(self, response: str, target_language: str, user_input: str = None) -> str:
        if target_language == 'en':
            return response

        language_prefixes = {
            'hi': '🏥 स्वास्थ्य सहायता:',
            'bn': '🏥 স্বাস্থ্য সহায়তা:',
            'te': '🏥 ఆరోగ్య సహాయం:',
            'ta': '🏥 சுகாதார உதவி:',
            'gu': '🏥 આરોગ્ય સહાય:',
            'kn': '🏥 ಆರೋಗ್ಯ ಸಹಾಯ:',
            'ml': '🏥 ആരോഗ്യ സഹായം:',
            'mr': '🏥 आरोग्य मदत:',
            'pa': '🏥 ਸਿਹਤ ਸਹਾਇਤਾ:',
            'ur': '🏥 صحت کی مدد:'
        }

        translated_response = self.translate_text(response, target_language)
        prefix = language_prefixes.get(target_language, '🏥 Health Assistant:')

        return f"{prefix}\n\n{translated_response}"

    def get_supported_languages_info(self) -> Dict:
        return {
            'total_supported': len(self.SUPPORTED_LANGUAGES),
            'languages': self.SUPPORTED_LANGUAGES,
            'google_translate_enabled': self.google_client is not None,
            'healthcare_terms_available': len(self.HEALTHCARE_TRANSLATIONS)
        }

# Global instance
translation_service = TranslationService()

if __name__ == "__main__":
    # Basic test of detection and translation
    print("🔧 Testing Translation Service...")
    texts = [
        ("I have fever", "hi"),
        ("headache", "bn"),
        ("doctor", "te"),
        ("please help", "ta")
    ]
    for text, lang in texts:
        detected = translation_service.detect_language(text)
        translated = translation_service.translate_text(text, lang)
        print(f"'{text}' -> {lang}: '{translated}'")
    print("✅ Translation test completed")