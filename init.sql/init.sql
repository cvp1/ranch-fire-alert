-- PostgreSQL initialization script for Ranch Fire Alert System
-- This script runs when the PostgreSQL container is first created

-- Create database if it doesn't exist (this is handled by POSTGRES_DB env var)
-- CREATE DATABASE ranch_alerts;

-- Connect to the ranch_alerts database
\c ranch_alerts;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';

-- Create initial ranch data
INSERT INTO ranch (name, latitude, longitude, radius_miles) 
VALUES ('Dragoon Mountain Ranch', 31.9190, -109.9673, 10.0)
ON CONFLICT (id) DO NOTHING;

-- Create admin user (password: admin123)
INSERT INTO "user" (name, email, password_hash, ranch_id, is_admin, created_at)
VALUES (
    'Admin User', 
    'admin@ranch.local', 
    '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', -- admin123
    1, 
    true, 
    CURRENT_TIMESTAMP
)
ON CONFLICT (email) DO NOTHING;

-- Log initialization
\echo 'Ranch Fire Alert System database initialized successfully' 