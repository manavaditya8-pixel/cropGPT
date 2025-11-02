-- CropGPT Initial Database Schema
-- Creates all necessary tables for the farmer assistant application

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom enum types
CREATE TYPE language_enum AS ENUM ('en', 'hi');
CREATE TYPE alert_type_enum AS ENUM ('above', 'below', 'change_percent');
CREATE TYPE application_status_enum AS ENUM ('applied', 'approved', 'rejected', 'pending');
CREATE TYPE scheme_category_enum AS ENUM ('financial_assistance', 'insurance', 'subsidy', 'equipment', 'training');

-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    preferred_language language_enum DEFAULT 'en' NOT NULL,
    location_state VARCHAR(100) DEFAULT 'Jharkhand' NOT NULL,
    location_district VARCHAR(100),
    land_size DECIMAL(10, 2), -- in hectares
    primary_crops TEXT[], -- array of crop names
    is_farmer BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    CONSTRAINT users_phone_number_check CHECK (phone_number ~ '^\+?[0-9]{10,15}$'),
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' OR email IS NULL),
    CONSTRAINT users_land_size_check CHECK (land_size > 0 OR land_size IS NULL)
);

-- Chat Conversations Table
CREATE TABLE chat_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255) NOT NULL,
    language language_enum NOT NULL,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    context_tags TEXT[],
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    response_time_ms INTEGER,
    user_feedback INTEGER CHECK (user_feedback >= 1 AND user_feedback <= 5)
);

-- Create indexes for chat conversations
CREATE INDEX idx_chat_conversations_user_session ON chat_conversations(user_id, session_id);
CREATE INDEX idx_chat_conversations_timestamp ON chat_conversations(timestamp DESC);
CREATE INDEX idx_chat_conversations_session_id ON chat_conversations(session_id);

-- Crop Prices Table
CREATE TABLE crop_prices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    commodity_name VARCHAR(255) NOT NULL,
    commodity_name_hi VARCHAR(255),
    variety VARCHAR(255),
    grade VARCHAR(50),
    market_name VARCHAR(255) NOT NULL,
    market_name_hi VARCHAR(255),
    state VARCHAR(100) DEFAULT 'Jharkhand' NOT NULL,
    min_price DECIMAL(10, 2) NOT NULL,
    max_price DECIMAL(10, 2) NOT NULL,
    modal_price DECIMAL(10, 2) NOT NULL,
    price_unit VARCHAR(50) DEFAULT 'Quintal' NOT NULL,
    arrival_date DATE NOT NULL,
    source VARCHAR(100), -- 'agmarknet', 'enam'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT crop_prices_price_check CHECK (min_price > 0 AND max_price > 0 AND modal_price > 0),
    CONSTRAINT crop_prices_price_order_check CHECK (min_price <= modal_price AND modal_price <= max_price)
);

-- Create indexes for crop prices
CREATE INDEX idx_crop_prices_commodity_date ON crop_prices(commodity_name, arrival_date DESC);
CREATE INDEX idx_crop_prices_market_date ON crop_prices(market_name, arrival_date DESC);
CREATE INDEX idx_crop_prices_state_date ON crop_prices(state, arrival_date DESC);
CREATE INDEX idx_crop_prices_arrival_date ON crop_prices(arrival_date DESC);

-- Weather Data Table
CREATE TABLE weather_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location_name VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    observation_time TIMESTAMP WITH TIME ZONE NOT NULL,
    temperature_celsius DECIMAL(5, 2) NOT NULL,
    feels_like_celsius DECIMAL(5, 2),
    humidity_percent INTEGER NOT NULL,
    rainfall_mm DECIMAL(5, 2) DEFAULT 0 NOT NULL,
    wind_speed_kph DECIMAL(5, 2),
    uv_index INTEGER,
    weather_condition VARCHAR(255) NOT NULL,
    weather_condition_hi VARCHAR(255),
    source VARCHAR(100) DEFAULT 'openweathermap' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT weather_data_temp_check CHECK (temperature_celsius >= -50 AND temperature_celsius <= 60),
    CONSTRAINT weather_data_humidity_check CHECK (humidity_percent >= 0 AND humidity_percent <= 100),
    CONSTRAINT weather_data_rainfall_check CHECK (rainfall_mm >= 0),
    CONSTRAINT weather_data_wind_check CHECK (wind_speed_kph >= 0),
    CONSTRAINT weather_data_uv_check CHECK (uv_index >= 0 AND uv_index <= 15)
);

-- Create indexes for weather data
CREATE INDEX idx_weather_data_location_time ON weather_data(location_name, observation_time DESC);
CREATE INDEX idx_weather_data_observation_time ON weather_data(observation_time DESC);
CREATE INDEX idx_weather_data_source ON weather_data(source);

-- Government Schemes Table
CREATE TABLE government_schemes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scheme_code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    name_hi VARCHAR(500),
    description TEXT NOT NULL,
    description_hi TEXT,
    category scheme_category_enum NOT NULL,
    implementing_agency VARCHAR(255),
    benefit_amount DECIMAL(12, 2),
    benefit_frequency VARCHAR(50), -- 'one_time', 'annual', 'monthly'
    eligibility_criteria TEXT NOT NULL,
    eligibility_criteria_hi TEXT,
    application_process TEXT NOT NULL,
    application_process_hi TEXT,
    required_documents TEXT[] NOT NULL,
    application_link VARCHAR(1000),
    deadline_date DATE,
    is_active BOOLEAN DEFAULT true NOT NULL,
    state VARCHAR(100) DEFAULT 'Jharkhand' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT government_schemes_benefit_check CHECK (benefit_amount > 0 OR benefit_amount IS NULL)
);

-- Create indexes for government schemes
CREATE INDEX idx_schemes_category ON government_schemes(category);
CREATE INDEX idx_schemes_active ON government_schemes(is_active);
CREATE INDEX idx_schemes_deadline ON government_schemes(deadline_date);
CREATE INDEX idx_schemes_state ON government_schemes(state);
CREATE INDEX idx_schemes_scheme_code ON government_schemes(scheme_code);

-- User Scheme Applications Table
CREATE TABLE user_scheme_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scheme_id UUID NOT NULL REFERENCES government_schemes(id) ON DELETE CASCADE,
    application_date DATE NOT NULL,
    status application_status_enum DEFAULT 'applied' NOT NULL,
    notes TEXT,
    reminder_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT user_scheme_applications_date_check CHECK (application_date <= CURRENT_DATE),
    CONSTRAINT user_scheme_applications_reminder_check CHECK (reminder_date >= application_date OR reminder_date IS NULL)
);

-- Create indexes for user scheme applications
CREATE INDEX idx_user_scheme_applications_user ON user_scheme_applications(user_id);
CREATE INDEX idx_user_scheme_applications_status ON user_scheme_applications(status);
CREATE INDEX idx_user_scheme_applications_scheme ON user_scheme_applications(scheme_id);

-- Price Alerts Table
CREATE TABLE price_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    commodity_name VARCHAR(255) NOT NULL,
    market_name VARCHAR(255) NOT NULL,
    alert_type alert_type_enum NOT NULL,
    threshold_value DECIMAL(10, 2) NOT NULL,
    change_percentage DECIMAL(5, 2),
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT price_alerts_threshold_check CHECK (threshold_value > 0),
    CONSTRAINT price_alerts_percentage_check CHECK (change_percentage > 0 OR change_percentage IS NULL)
);

-- Create indexes for price alerts
CREATE INDEX idx_price_alerts_user ON price_alerts(user_id);
CREATE INDEX idx_price_alerts_commodity ON price_alerts(commodity_name);
CREATE INDEX idx_price_alerts_active ON price_alerts(is_active);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_government_schemes_updated_at BEFORE UPDATE ON government_schemes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data (optional - can be removed in production)
INSERT INTO users (phone_number, name, preferred_language, location_state, location_district, land_size, primary_crops) VALUES
('+919876543210', 'रमेश कुमार', 'hi', 'Jharkhand', 'Ranchi', 2.5, ARRAY['paddy', 'wheat']),
('+919876543211', 'Sunita Devi', 'en', 'Jharkhand', 'Jamshedpur', 1.8, ARRAY['paddy', 'pulses']),
('+919876543212', 'मोहन सिंह', 'hi', 'Jharkhand', 'Dhanbad', 3.2, ARRAY['maize', 'pulses', 'oilseeds']);

-- Insert sample government schemes
INSERT INTO government_schemes (scheme_code, name, name_hi, description, description_hi, category, benefit_amount, benefit_frequency, eligibility_criteria, eligibility_criteria_hi, required_documents, application_link, deadline_date, implementing_agency) VALUES
('PM-KISAN-001', 'Pradhan Mantri Kisan Samman Nidhi', 'प्रधानमंत्री किसान सम्मान निधि', 'Income support of ₹6,000 per year to farmer families', 'प्रति वर्ष ₹6,000 की आय सहायता किसान परिवारों को', 'financial_assistance', 6000.00, 'annual', 'Small and marginal farmers', 'छोटे और सीमांत किसान', ARRAY['Aadhaar', 'Land records', 'Bank account'], 'https://pmkisan.gov.in/', '2024-12-31', 'Ministry of Agriculture'),
('PMFBY-001', 'Pradhan Mantri Fasal Bima Yojana', 'प्रधानमंत्री फसल बीमा योजना', 'Crop insurance scheme for farmers against weather-related losses', 'मौसम संबंधी नुकसान के खिलाफ किसानों के लिए फसल बीमा योजना', 'insurance', NULL, NULL, 'All farmers growing notified crops', 'सूचित फसलें उगाने वाले सभी किसान', ARRAY['Aadhaar', 'Land records', 'Bank account', 'Crop details'], 'https://pmfby.gov.in/', '2024-11-30', 'Ministry of Agriculture');

-- Create view for active schemes
CREATE VIEW active_schemes AS
SELECT * FROM government_schemes
WHERE is_active = true
AND (deadline_date IS NULL OR deadline_date >= CURRENT_DATE)
ORDER BY deadline_date ASC NULLS LAST;

-- Create view for user statistics
CREATE VIEW user_statistics AS
SELECT
    COUNT(*) as total_users,
    COUNT(CASE WHEN is_farmer = true THEN 1 END) as farmers_count,
    COUNT(CASE WHEN preferred_language = 'hi' THEN 1 END) as hindi_users,
    COUNT(CASE WHEN preferred_language = 'en' THEN 1 END) as english_users,
    AVG(land_size) as avg_land_size,
    location_state
FROM users
GROUP BY location_state;

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cropgpt_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cropgpt_user;

-- Create indexes for better performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_location_state ON users(location_state);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_preferred_language ON users(preferred_language);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_is_farmer ON users(is_farmer);

-- Create index for full-text search on schemes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_schemes_name_search ON government_schemes USING gin(to_tsvector('english', name || ' ' || description));
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_schemes_name_hi_search ON government_schemes USING gin(to_tsvector('simple', COALESCE(name_hi, '') || ' ' || COALESCE(description_hi, '')));

-- Final verification query
SELECT
    'users' as table_name, COUNT(*) as row_count FROM users
UNION ALL
SELECT
    'government_schemes' as table_name, COUNT(*) as row_count FROM government_schemes
UNION ALL
SELECT
    'crop_prices' as table_name, COUNT(*) as row_count FROM crop_prices
UNION ALL
SELECT
    'weather_data' as table_name, COUNT(*) as row_count FROM weather_data
UNION ALL
SELECT
    'chat_conversations' as table_name, COUNT(*) as row_count FROM chat_conversations
ORDER BY table_name;