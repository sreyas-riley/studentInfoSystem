#!/usr/bin/env python3
"""
Database migration script to add new attendance columns
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Migrate database to add new attendance columns"""
    try:
        # Initialize Supabase client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully")
        
        # Check if attendance table exists and add new columns
        try:
            # Try to add new columns to attendance table
            migration_sql = """
            ALTER TABLE attendance 
            ADD COLUMN IF NOT EXISTS attempts_remaining INTEGER DEFAULT 3,
            ADD COLUMN IF NOT EXISTS attempt_history JSONB DEFAULT '[]',
            ADD COLUMN IF NOT EXISTS final_status VARCHAR(50) DEFAULT 'pending';
            """
            
            # Execute migration
            result = supabase.rpc('exec_sql', {'sql': migration_sql}).execute()
            logger.info("Database migration completed successfully")
            
        except Exception as e:
            logger.warning(f"Migration warning (this is normal if columns already exist): {e}")
            
        # Verify the table structure
        try:
            # Check if we can query the new columns
            test_query = supabase.table('attendance').select('attempts_remaining, attempt_history, final_status').limit(1).execute()
            logger.info("✅ New attendance columns are working correctly")
        except Exception as e:
            logger.error(f"❌ Error verifying new columns: {e}")
            raise
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate_database() 