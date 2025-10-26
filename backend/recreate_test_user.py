"""
Delete test user and recreate without email confirmation
"""
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TEST_EMAIL = "test@agrovision.com"
TEST_PASSWORD = "test123456"

print("Creating new test user (without email confirmation)...")
print(f"Email: {TEST_EMAIL}")
print(f"Password: {TEST_PASSWORD}")

try:
    # Sign up new user
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
        print(f"Email confirmed: {response.user.email_confirmed_at is not None}")
        print(f"\nYou can now login with:")
        print(f"Email: {TEST_EMAIL}")
        print(f"Password: {TEST_PASSWORD}")
    else:
        print("\n❌ Failed to create user")
        
except Exception as e:
    error_msg = str(e)
    if "already registered" in error_msg.lower() or "already been registered" in error_msg.lower():
        print(f"\n⚠️ User already exists!")
        print(f"\nTrying to sign in to check confirmation status...")
        try:
            login = supabase.auth.sign_in_with_password({
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            print(f"✅ Login successful! User is confirmed.")
            print(f"User ID: {login.user.id}")
        except Exception as login_error:
            print(f"❌ Login failed: {login_error}")
            print(f"\n🔧 SOLUTION: Go to Supabase Dashboard and:")
            print(f"1. Delete the existing user manually")
            print(f"2. Or confirm their email manually")
            print(f"3. Then run this script again")
    else:
        print(f"\n❌ Error: {error_msg}")
