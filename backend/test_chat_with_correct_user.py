import requests
import json

# Test chat API with correct user ID
resp = requests.post(
    'http://localhost:8000/api/chat',
    json={
        'message': 'My rice crops are turning yellow. What should I do?',
        'farm_id': '10000000-0000-0000-0000-000000000001',  # Green Valley Farm
        'user_id': '00000000-0000-0000-0000-000000000001'   # Test Farmer
    }
)

print(f'Status: {resp.status_code}')
print(f'\nResponse:')
print(json.dumps(resp.json(), indent=2))

# Check database
from services.supabase_client import get_supabase_client
supabase = get_supabase_client()
chats = supabase.table("chat_history").select("*").execute()

print(f'\n\nTotal chats in database: {len(chats.data)}')
print('Latest 3 chats:')
for chat in chats.data[-3:]:
    print(f'  - {chat["message"][:60]}...')
