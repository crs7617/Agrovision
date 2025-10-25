-- AgroVision Database Schema
-- Execute this in Supabase SQL Editor: https://supabase.com/dashboard/project/_/sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. USERS TABLE (for authentication and user management)
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster email lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- =====================================================
-- 2. FARMS TABLE (farm information and metadata)
-- =====================================================
CREATE TABLE IF NOT EXISTS farms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    crop_type VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    area DECIMAL(10, 2), -- in hectares
    location_address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_farms_user_id ON farms(user_id);
CREATE INDEX IF NOT EXISTS idx_farms_crop_type ON farms(crop_type);
-- Geospatial index (optional - requires earthdistance extension)
-- CREATE INDEX IF NOT EXISTS idx_farms_location ON farms(latitude, longitude);

-- =====================================================
-- 3. SATELLITE_ANALYSIS TABLE (analysis results)
-- =====================================================
CREATE TABLE IF NOT EXISTS satellite_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID REFERENCES farms(id) ON DELETE CASCADE,
    ndvi DECIMAL(5, 4), -- 0.0000 to 1.0000
    evi DECIMAL(5, 4),
    savi DECIMAL(5, 4),
    ndwi DECIMAL(5, 4),
    health_score INTEGER CHECK (health_score >= 0 AND health_score <= 100),
    issues TEXT[], -- array of detected issues
    field_count INTEGER,
    healthy_percentage DECIMAL(5, 2),
    stressed_percentage DECIMAL(5, 2),
    bare_soil_percentage DECIMAL(5, 2),
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_satellite_farm_id ON satellite_analysis(farm_id);
CREATE INDEX IF NOT EXISTS idx_satellite_analyzed_at ON satellite_analysis(analyzed_at DESC);

-- =====================================================
-- 4. CHAT_HISTORY TABLE (conversational AI logs)
-- =====================================================
CREATE TABLE IF NOT EXISTS chat_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    farm_id UUID REFERENCES farms(id) ON DELETE SET NULL,
    message TEXT NOT NULL,
    response_text TEXT NOT NULL,
    suggestions TEXT[], -- array of suggestions
    intent VARCHAR(100),
    entities JSONB, -- flexible JSON for extracted entities
    confidence VARCHAR(20), -- high, medium, low
    source VARCHAR(50), -- llm, rule_based
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_chat_user_id ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_farm_id ON chat_history(farm_id);
CREATE INDEX IF NOT EXISTS idx_chat_timestamp ON chat_history(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_chat_intent ON chat_history(intent);

-- =====================================================
-- 5. RECOMMENDATIONS TABLE (AI-generated recommendations)
-- =====================================================
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID REFERENCES farms(id) ON DELETE CASCADE,
    analysis_id UUID REFERENCES satellite_analysis(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) CHECK (priority IN ('high', 'medium', 'low')),
    category VARCHAR(100), -- irrigation, fertilization, pest_control, etc.
    estimated_cost DECIMAL(10, 2), -- in INR
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'dismissed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_recommendations_farm_id ON recommendations(farm_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_priority ON recommendations(priority);
CREATE INDEX IF NOT EXISTS idx_recommendations_status ON recommendations(status);

-- =====================================================
-- 6. WEATHER_LOGS TABLE (weather data cache)
-- =====================================================
CREATE TABLE IF NOT EXISTS weather_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID REFERENCES farms(id) ON DELETE CASCADE,
    temperature DECIMAL(5, 2),
    humidity INTEGER,
    rainfall DECIMAL(6, 2),
    wind_speed DECIMAL(5, 2),
    description VARCHAR(255),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_weather_farm_id ON weather_logs(farm_id);
CREATE INDEX IF NOT EXISTS idx_weather_recorded_at ON weather_logs(recorded_at DESC);

-- =====================================================
-- 7. TEMPORAL_DATA TABLE (historical NDVI/indices)
-- =====================================================
CREATE TABLE IF NOT EXISTS temporal_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID REFERENCES farms(id) ON DELETE CASCADE,
    metric_type VARCHAR(50) NOT NULL, -- NDVI, EVI, SAVI, etc.
    value DECIMAL(5, 4) NOT NULL,
    is_anomaly BOOLEAN DEFAULT FALSE,
    anomaly_type VARCHAR(50), -- sudden_drop, sudden_increase, outlier
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_temporal_farm_id ON temporal_data(farm_id);
CREATE INDEX IF NOT EXISTS idx_temporal_metric_type ON temporal_data(metric_type);
CREATE INDEX IF NOT EXISTS idx_temporal_timestamp ON temporal_data(timestamp DESC);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE farms ENABLE ROW LEVEL SECURITY;
ALTER TABLE satellite_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE weather_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE temporal_data ENABLE ROW LEVEL SECURITY;

-- Users can read their own profile
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Users can view their own farms
CREATE POLICY "Users can view own farms" ON farms
    FOR SELECT USING (auth.uid() = user_id);

-- Users can insert their own farms
CREATE POLICY "Users can create own farms" ON farms
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own farms
CREATE POLICY "Users can update own farms" ON farms
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can delete their own farms
CREATE POLICY "Users can delete own farms" ON farms
    FOR DELETE USING (auth.uid() = user_id);

-- Users can view analysis for their farms
CREATE POLICY "Users can view own farm analysis" ON satellite_analysis
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM farms 
            WHERE farms.id = satellite_analysis.farm_id 
            AND farms.user_id = auth.uid()
        )
    );

-- Service role can insert analysis (backend API)
CREATE POLICY "Service can insert analysis" ON satellite_analysis
    FOR INSERT WITH CHECK (true);

-- Users can view their chat history
CREATE POLICY "Users can view own chat" ON chat_history
    FOR SELECT USING (auth.uid() = user_id);

-- Users can insert their own chats
CREATE POLICY "Users can create own chat" ON chat_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Similar policies for other tables...
CREATE POLICY "Users can view own recommendations" ON recommendations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM farms 
            WHERE farms.id = recommendations.farm_id 
            AND farms.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can view own weather" ON weather_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM farms 
            WHERE farms.id = weather_logs.farm_id 
            AND farms.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can view own temporal data" ON temporal_data
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM farms 
            WHERE farms.id = temporal_data.farm_id 
            AND farms.user_id = auth.uid()
        )
    );

-- =====================================================
-- FUNCTIONS & TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users table
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for farms table
CREATE TRIGGER update_farms_updated_at BEFORE UPDATE ON farms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SEED DATA (optional - for testing)
-- =====================================================

-- Insert a test user (you can delete this later)
INSERT INTO users (id, email, name) VALUES 
    ('00000000-0000-0000-0000-000000000001', 'test@agrovision.com', 'Test Farmer')
ON CONFLICT (email) DO NOTHING;

-- Insert test farms
INSERT INTO farms (id, user_id, name, crop_type, latitude, longitude, area) VALUES
    ('10000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'Green Valley Farm', 'wheat', 28.6139, 77.2090, 5.5),
    ('10000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'Sunrise Cotton Fields', 'cotton', 23.0225, 72.5714, 8.2),
    ('10000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', 'River Rice Plantation', 'rice', 17.3850, 78.4867, 12.0)
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================
DO $$
BEGIN
    RAISE NOTICE '✓ AgroVision database schema created successfully!';
    RAISE NOTICE '✓ Tables: users, farms, satellite_analysis, chat_history, recommendations, weather_logs, temporal_data';
    RAISE NOTICE '✓ RLS policies enabled for security';
    RAISE NOTICE '✓ Seed data inserted (test user + 3 farms)';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Enable authentication in Supabase Dashboard';
    RAISE NOTICE '2. Update backend to use Supabase client';
    RAISE NOTICE '3. Test API endpoints with real database';
END $$;
