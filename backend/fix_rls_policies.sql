-- Fix RLS Policies for Backend API Access
-- Run this in Supabase SQL Editor after creating the schema

-- Drop existing restrictive policies
DROP POLICY IF EXISTS "Users can view own profile" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;
DROP POLICY IF EXISTS "Users can view own farms" ON farms;
DROP POLICY IF EXISTS "Users can create own farms" ON farms;
DROP POLICY IF EXISTS "Users can update own farms" ON farms;
DROP POLICY IF EXISTS "Users can delete own farms" ON farms;
DROP POLICY IF EXISTS "Users can view own farm analysis" ON satellite_analysis;
DROP POLICY IF EXISTS "Service can insert analysis" ON satellite_analysis;
DROP POLICY IF EXISTS "Users can view own chat" ON chat_history;
DROP POLICY IF EXISTS "Users can create own chat" ON chat_history;
DROP POLICY IF EXISTS "Users can view own recommendations" ON recommendations;
DROP POLICY IF EXISTS "Users can view own weather" ON weather_logs;
DROP POLICY IF EXISTS "Users can view own temporal data" ON temporal_data;

-- Create permissive policies for backend API (using service role key)
-- These allow full access when using the anon key (for development)

-- Users table - allow all operations
CREATE POLICY "Allow all operations on users" ON users
    FOR ALL USING (true) WITH CHECK (true);

-- Farms table - allow all operations
CREATE POLICY "Allow all operations on farms" ON farms
    FOR ALL USING (true) WITH CHECK (true);

-- Satellite analysis - allow all operations
CREATE POLICY "Allow all operations on satellite_analysis" ON satellite_analysis
    FOR ALL USING (true) WITH CHECK (true);

-- Chat history - allow all operations
CREATE POLICY "Allow all operations on chat_history" ON chat_history
    FOR ALL USING (true) WITH CHECK (true);

-- Recommendations - allow all operations
CREATE POLICY "Allow all operations on recommendations" ON recommendations
    FOR ALL USING (true) WITH CHECK (true);

-- Weather logs - allow all operations
CREATE POLICY "Allow all operations on weather_logs" ON weather_logs
    FOR ALL USING (true) WITH CHECK (true);

-- Temporal data - allow all operations
CREATE POLICY "Allow all operations on temporal_data" ON temporal_data
    FOR ALL USING (true) WITH CHECK (true);

-- Re-insert seed data (now that RLS allows it)
INSERT INTO users (id, email, name) VALUES 
    ('00000000-0000-0000-0000-000000000001', 'test@agrovision.com', 'Test Farmer')
ON CONFLICT (email) DO NOTHING;

INSERT INTO farms (id, user_id, name, crop_type, latitude, longitude, area) VALUES
    ('10000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'Green Valley Farm', 'wheat', 28.6139, 77.2090, 5.5),
    ('10000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'Sunrise Cotton Fields', 'cotton', 23.0225, 72.5714, 8.2),
    ('10000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', 'River Rice Plantation', 'rice', 17.3850, 78.4867, 12.0)
ON CONFLICT (id) DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✓ RLS policies updated for backend API access!';
    RAISE NOTICE '✓ Seed data inserted successfully!';
    RAISE NOTICE '✓ Backend can now read/write data freely';
    RAISE NOTICE '';
    RAISE NOTICE 'NOTE: For production, implement proper authentication-based RLS';
END $$;
