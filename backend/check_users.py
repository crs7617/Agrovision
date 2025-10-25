from services.supabase_client import get_supabase_client

supabase = get_supabase_client()
users = supabase.table('users').select('id, email, name').execute()

print('\nUsers in database:')
for u in users.data:
    print(f'  - {u["name"]} ({u["email"]}): {u["id"]}')
