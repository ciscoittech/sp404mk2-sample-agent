-- PostgreSQL Initialization Script for SP404 MK2 Sample Agent
-- This script runs automatically when the PostgreSQL container first starts

-- Enable UUID extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable trigram extension for full-text search (fuzzy matching)
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Set timezone to UTC for consistency
SET timezone = 'UTC';

-- Log successful initialization
DO $$
BEGIN
  RAISE NOTICE 'PostgreSQL initialized successfully for SP404 MK2 Sample Agent';
  RAISE NOTICE 'Extensions enabled: uuid-ossp, pg_trgm';
END $$;
