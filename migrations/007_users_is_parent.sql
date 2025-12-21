-- Add is_parent column to users table
-- This allows marking users as parents with admin privileges

ALTER TABLE users ADD COLUMN is_parent INTEGER DEFAULT 0;
