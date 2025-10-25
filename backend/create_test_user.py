"""
Create a test user in Supabase for development
Run this script to create a test account
"""
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test user credentials
TEST_EMAIL = "test@agrovision.com"
TEST_PASSWORD = "test123456"

print("Creating test user...")
print(f"Email: {TEST_EMAIL}")
print(f"Password: {TEST_PASSWORD}")

try:
    # Try to sign up the user
    response = supabase.auth.sign_up({
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "options": {
            "data": {
                "name": "Test User"
            }
        }
    })
    
    if response.user:
        print(f"\n✅ Test user created successfully!")
        print(f"User ID: {response.user.id}")
        print(f"\nYou can now login with:")
        print(f"Email: {TEST_EMAIL}")
        print(f"Password: {TEST_PASSWORD}")
    else:
        print("\n❌ Failed to create user")
        
except Exception as e:
    error_msg = str(e)
    if "already registered" in error_msg.lower() or "already exists" in error_msg.lower():
        print(f"\n✅ Test user already exists!")
        print(f"You can login with:")
        print(f"Email: {TEST_EMAIL}")
        print(f"Password: {TEST_PASSWORD}")
    else:
        print(f"\n❌ Error: {error_msg}")
