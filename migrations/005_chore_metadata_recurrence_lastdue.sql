-- Migration: Add recurrence and last_due_iso columns to chore_metadata
ALTER TABLE chore_metadata ADD COLUMN recurrence TEXT;
ALTER TABLE chore_metadata ADD COLUMN last_due_iso TEXT;
