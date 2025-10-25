"""
Quick test to verify database integration
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.supabase_client import get_supabase_client

def check_chat_history():
    """Check if chat was saved"""
    print("\n=== Checking Chat History in Database ===\n")
    
    supabase = get_supabase_client()
    
    # Get all chats
    result = supabase.table("chat_history").select("*").limit(10).execute()
    
    print(f"Total chats in database: {len(result.data)}")
    
    for chat in result.data:
        print(f"\n  ID: {chat['id'][:20]}...")
        print(f"  Message: {chat['message'][:50]}...")
        print(f"  Intent: {chat['intent']}")
        print(f"  Timestamp: {chat['timestamp']}")

def check_farms():
    """Check farms in database"""
    print("\n=== Checking Farms in Database ===\n")
    
    supabase = get_supabase_client()
    
    result = supabase.table("farms").select("*").execute()
    
    print(f"Total farms: {len(result.data)}")
    
    for farm in result.data:
        print(f"\n  • {farm['name']} ({farm['crop_type']})")
        print(f"    Location: {farm['latitude']}, {farm['longitude']}")
        print(f"    ID: {farm['id'][:20]}...")

def check_temporal_data():
    """Check temporal data"""
    print("\n=== Checking Temporal Data ===\n")
    
    supabase = get_supabase_client()
    
    result = supabase.table("temporal_data").select("*").limit(10).execute()
    
    print(f"Total temporal data points: {len(result.data)}")
    
    for point in result.data[:5]:
        print(f"\n  Metric: {point['metric_type']}")
        print(f"  Value: {point['value']}")
        print(f"  Timestamp: {point['timestamp']}")

if __name__ == "__main__":
    check_farms()
    check_chat_history()
    check_temporal_data()
    print("\n" + "="*60 + "\n")
