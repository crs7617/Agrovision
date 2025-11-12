"""
Local test script for AI Chatbot
Tests the complete chat flow including GROQ and Gemini translation
"""
import os
import sys
sys.path.append('backend')

from dotenv import load_dotenv
load_dotenv('backend/.env')

# Test environment variables
print("=" * 60)
print("ENVIRONMENT VARIABLES CHECK")
print("=" * 60)
groq_key = os.getenv('GROQ_API_KEY')
google_key = os.getenv('GOOGLE_API_KEY')

print(f"GROQ_API_KEY: {'✓ SET (' + groq_key[:20] + '...)' if groq_key else '✗ NOT SET'}")
print(f"GOOGLE_API_KEY: {'✓ SET (' + google_key[:20] + '...)' if google_key else '✗ NOT SET'}")
print()

# Test GROQ API
print("=" * 60)
print("TESTING GROQ API (LLaMA 3.1)")
print("=" * 60)
from services.llm_service import call_groq_api

test_response = call_groq_api(
    "What crops grow well in summer in India?",
    "You are an agricultural expert. Answer briefly."
)

if test_response:
    print("✓ GROQ API WORKING!")
    print(f"Response: {test_response[:100]}...")
else:
    print("✗ GROQ API FAILED!")
print()

# Test Google Gemini Translation
print("=" * 60)
print("TESTING GOOGLE GEMINI TRANSLATION")
print("=" * 60)
from services.translation_service import translation_service

test_hindi = "गर्मियों में कौन सी फसलें उगाई जाती हैं?"
english_translation = translation_service.translate_to_english(test_hindi, 'hi')
print(f"Hindi: {test_hindi}")
print(f"English: {english_translation}")

if english_translation != test_hindi:
    print("✓ TRANSLATION TO ENGLISH WORKING!")
else:
    print("✗ TRANSLATION FAILED - API KEY ISSUE!")

# Translate back
hindi_back = translation_service.translate_from_english("Summer crops include rice and cotton", 'hi')
print(f"English: Summer crops include rice and cotton")
print(f"Hindi: {hindi_back}")
print()

# Test complete chat flow
print("=" * 60)
print("TESTING COMPLETE CHAT FLOW")
print("=" * 60)
from services.chat_service import parse_farmer_query, generate_response

# Parse query
query = "What should I do if my wheat crop leaves are yellowing?"
parsed = parse_farmer_query(query)
print(f"Query: {query}")
print(f"Intent: {parsed['intent']}")
print(f"Entities: {parsed['entities']}")
print()

# Generate response
response = generate_response(query, "", parsed['intent'], parsed['entities'])
print(f"Response Source: {response['source']}")
print(f"Response: {response['response_text'][:150]}...")
print(f"Suggestions: {response['suggestions']}")
print()

# Test with Hindi
print("=" * 60)
print("TESTING HINDI CHAT")
print("=" * 60)
hindi_query = "मेरी फसल पीली क्यों हो रही है?"
print(f"Hindi Query: {hindi_query}")

# Translate to English
english_query = translation_service.translate_to_english(hindi_query, 'hi')
print(f"Translated to English: {english_query}")

# Get response
parsed_hindi = parse_farmer_query(english_query)
response_hindi = generate_response(english_query, "", parsed_hindi['intent'], parsed_hindi['entities'])
print(f"English Response: {response_hindi['response_text'][:100]}...")

# Translate back to Hindi
hindi_response = translation_service.translate_from_english(response_hindi['response_text'], 'hi')
print(f"Hindi Response: {hindi_response[:100]}...")
print()

print("=" * 60)
print("ALL TESTS COMPLETE!")
print("=" * 60)
