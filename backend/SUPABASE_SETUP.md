# Supabase Setup Guide for AgroVision

## Step 1: Execute Database Schema

1. **Open Supabase Dashboard**
   - Go to: https://supabase.com/dashboard
   - Select your project: `fpagxlomlturzoffctdk`

2. **Navigate to SQL Editor**
   - Click on "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Copy & Paste Schema**
   - Open `backend/supabase_schema.sql`
   - Copy ALL the SQL code
   - Paste into Supabase SQL Editor
   - Click "Run" button (bottom right)

4. **Verify Tables Created**
   - Go to "Table Editor" in left sidebar
   - You should see 7 tables:
     ✓ users
     ✓ farms
     ✓ satellite_analysis
     ✓ chat_history
     ✓ recommendations
     ✓ weather_logs
     ✓ temporal_data

## Step 2: Enable Authentication (Optional for now)

You can enable auth later when building login page:
- Go to "Authentication" → "Providers"
- Enable "Email" provider
- (Optional) Enable Google/GitHub OAuth

## Step 3: Test Connection

Run this command in your backend terminal:

```bash
cd backend
python -c "from services.supabase_client import check_connection; check_connection()"
```

Should output: `✓ Supabase connection verified`

## Step 4: View Seed Data

In Supabase Table Editor:
- Click "farms" table
- You should see 3 test farms created
- Click "users" table  
- You should see 1 test user

## Troubleshooting

**Error: "relation farms does not exist"**
- Schema wasn't executed properly
- Re-run the SQL in Supabase SQL Editor

**Error: "insufficient_privilege"**
- Using wrong API key
- Make sure using `SUPABASE_KEY` (anon key) from `.env`

**Connection timeout**
- Check internet connection
- Verify `SUPABASE_URL` in `.env` is correct

## Next: Update Backend to Use Supabase

After schema is created, I'll update these files:
1. `routers/satellite.py` - Farm CRUD operations
2. `services/chat_service.py` - Chat persistence
3. `services/temporal_service.py` - Historical data
4. Add new `routers/farms.py` for farm management

---

**Ready to proceed?** Let me know once you've executed the SQL schema in Supabase!
