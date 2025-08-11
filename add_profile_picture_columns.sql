-- Add profile picture columns to existing students table
-- Run this in your Supabase SQL Editor

-- Add the new columns to the students table
ALTER TABLE students 
ADD COLUMN IF NOT EXISTS profile_picture TEXT,
ADD COLUMN IF NOT EXISTS has_profile_picture BOOLEAN DEFAULT FALSE;

-- Update existing students to have has_profile_picture = false
UPDATE students 
SET has_profile_picture = FALSE 
WHERE has_profile_picture IS NULL;

-- Verify the changes
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'students' 
AND column_name IN ('profile_picture', 'has_profile_picture')
ORDER BY column_name; 