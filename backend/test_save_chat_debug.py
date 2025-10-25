"""
Test save_chat function with debug output
"""
import sys
from services.chat_service import save_chat

# Test save_chat directly
print("\n=== Testing save_chat directly ===\n")

user_id = "00000000-0000-0000-0000-000000000001"  # Real user from database
farm_id = "10000000-0000-0000-0000-000000000001"  # Green Valley Farm
message = "What is the health of my crops?"
response = {
    "response_text": "Test response",
    "suggestions": ["Test suggestion"],
    "confidence_level": "high"
}
intent = "general_info"
entities = {}

result = save_chat(
    user_id=user_id,
    farm_id=farm_id,
    message=message,
    response=response,
    intent=intent,
    entities=entities
)

print("\n=== Result ===")
print(result)
print("\n=== Now checking database ===\n")

from services.supabase_client import get_supabase_client

supabase = get_supabase_client()
chats = supabase.table("chat_history").select("*").execute()
print(f"Total chats in database: {len(chats.data)}")
for chat in chats.data:
    print(f"  - Chat {chat['id']}: {chat['message'][:50]}")
