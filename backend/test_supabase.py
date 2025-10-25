"""
Test Supabase Integration
Verify database connection and basic operations
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.supabase_client import get_supabase_client, check_connection

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def test_connection():
    """Test 1: Basic connection"""
    print(f"\n{BLUE}{'='*60}")
    print("Test 1: Supabase Connection")
    print(f"{'='*60}{RESET}\n")
    
    try:
        connected = check_connection()
        if connected:
            print(f"{GREEN}✓ Connection successful!{RESET}")
            return True
        else:
            print(f"{RED}✗ Connection failed{RESET}")
            return False
    except Exception as e:
        print(f"{RED}✗ Error: {e}{RESET}")
        return False


def test_read_farms():
    """Test 2: Read farms from database"""
    print(f"\n{BLUE}{'='*60}")
    print("Test 2: Read Farms")
    print(f"{'='*60}{RESET}\n")
    
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("farms").select("*").limit(10).execute()
        
        farms = response.data
        print(f"{GREEN}✓ Retrieved {len(farms)} farms{RESET}\n")
        
        for farm in farms:
            print(f"  • {farm['name']} ({farm['crop_type']}) - ID: {farm['id'][:8]}...")
        
        return len(farms) > 0
        
    except Exception as e:
        print(f"{RED}✗ Error: {e}{RESET}")
        return False


def test_read_users():
    """Test 3: Read users from database"""
    print(f"\n{BLUE}{'='*60}")
    print("Test 3: Read Users")
    print(f"{'='*60}{RESET}\n")
    
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("users").select("*").limit(10).execute()
        
        users = response.data
        print(f"{GREEN}✓ Retrieved {len(users)} users{RESET}\n")
        
        for user in users:
            print(f"  • {user['name']} ({user['email']}) - ID: {user['id'][:8]}...")
        
        return len(users) > 0
        
    except Exception as e:
        print(f"{RED}✗ Error: {e}{RESET}")
        return False


def test_create_farm():
    """Test 4: Create a new farm"""
    print(f"\n{BLUE}{'='*60}")
    print("Test 4: Create Farm")
    print(f"{'='*60}{RESET}\n")
    
    try:
        supabase = get_supabase_client()
        
        farm_data = {
            "user_id": "00000000-0000-0000-0000-000000000001",
            "name": "Test Automation Farm",
            "crop_type": "wheat",
            "latitude": 28.5,
            "longitude": 77.3,
            "area": 3.5
        }
        
        response = supabase.table("farms").insert(farm_data).execute()
        
        if response.data:
            created_farm = response.data[0]
            print(f"{GREEN}✓ Farm created successfully!{RESET}")
            print(f"  ID: {created_farm['id']}")
            print(f"  Name: {created_farm['name']}")
            print(f"  Crop: {created_farm['crop_type']}")
            
            # Clean up - delete the test farm
            supabase.table("farms").delete().eq("id", created_farm['id']).execute()
            print(f"\n{YELLOW}  (Test farm deleted after creation){RESET}")
            
            return True
        else:
            print(f"{RED}✗ Failed to create farm{RESET}")
            return False
        
    except Exception as e:
        print(f"{RED}✗ Error: {e}{RESET}")
        return False


def test_tables_exist():
    """Test 5: Verify all tables exist"""
    print(f"\n{BLUE}{'='*60}")
    print("Test 5: Verify Database Schema")
    print(f"{'='*60}{RESET}\n")
    
    tables = [
        "users",
        "farms",
        "satellite_analysis",
        "chat_history",
        "recommendations",
        "weather_logs",
        "temporal_data"
    ]
    
    try:
        supabase = get_supabase_client()
        all_exist = True
        
        for table in tables:
            try:
                # Try to query each table
                supabase.table(table).select("id").limit(1).execute()
                print(f"{GREEN}✓{RESET} Table '{table}' exists")
            except Exception as e:
                print(f"{RED}✗{RESET} Table '{table}' missing or inaccessible")
                all_exist = False
        
        return all_exist
        
    except Exception as e:
        print(f"{RED}✗ Error: {e}{RESET}")
        return False


def run_all_tests():
    """Run all Supabase tests"""
    print(f"\n{BLUE}{'='*60}")
    print("SUPABASE INTEGRATION TEST SUITE")
    print(f"{'='*60}{RESET}")
    
    tests = [
        ("Connection Test", test_connection),
        ("Read Farms", test_read_farms),
        ("Read Users", test_read_users),
        ("Create Farm", test_create_farm),
        ("Verify Schema", test_tables_exist),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n{RED}Test '{test_name}' crashed: {e}{RESET}")
            results.append((test_name, False))
    
    # Print summary
    print(f"\n{BLUE}{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}{RESET}\n")
    
    passed_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for test_name, result in results:
        status = f"{GREEN}✓ PASSED{RESET}" if result else f"{RED}✗ FAILED{RESET}"
        print(f"{status} - {test_name}")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    
    if passed_count == total_count:
        print(f"{GREEN}ALL TESTS PASSED! ({passed_count}/{total_count}){RESET}")
        print(f"{GREEN}🎉 Supabase integration is working!{RESET}")
    else:
        print(f"{YELLOW}TESTS PASSED: {passed_count}/{total_count}{RESET}")
        print(f"{RED}Some tests failed. Check the output above.{RESET}")
    
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    return passed_count == total_count


if __name__ == "__main__":
    run_all_tests()
