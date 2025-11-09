import os
import google.generativeai as genai

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'ta': 'Tamil',
    'te': 'Telugu',
    'ml': 'Malayalam',
    'kn': 'Kannada',
    'bn': 'Bengali'
}

class TranslationService:
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
    
    def translate_to_english(self, text, source_lang):
        if source_lang == 'en' or not self.model:
            return text
        try:
            prompt = f'Translate this from {source_lang} to English. Return ONLY the translation: {text}'
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return text
    
    def translate_from_english(self, text, target_lang):
        if target_lang == 'en' or not self.model:
            return text
        try:
            prompt = f'Translate this English text to {target_lang}. Return ONLY the translation: {text}'
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return text

translation_service = TranslationService()
