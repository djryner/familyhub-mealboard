-- Migration: Add chore_metadata table for local chore metadata storage
CREATE TABLE IF NOT EXISTS chore_metadata (
    task_id VARCHAR PRIMARY KEY,
    assigned_to VARCHAR,
    -- priority column removed
    -- Add more fields as needed
);
