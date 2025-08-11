#!/usr/bin/env python3
"""
Update database schema to add profile picture columns
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def update_database_schema():
    """Update the database schema to add profile picture columns"""
    try:
        # Get environment variables
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials in .env file")
            return False
        
        print(f"🔗 Connecting to Supabase...")
        
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # SQL to add profile picture columns
        sql_commands = [
            """
            ALTER TABLE students 
            ADD COLUMN IF NOT EXISTS profile_picture TEXT,
            ADD COLUMN IF NOT EXISTS has_profile_picture BOOLEAN DEFAULT FALSE;
            """,
            """
            UPDATE students 
            SET has_profile_picture = FALSE 
            WHERE has_profile_picture IS NULL;
            """
        ]
        
        print("📊 Updating database schema...")
        
        for i, sql in enumerate(sql_commands, 1):
            print(f"Running command {i}...")
            try:
                # Execute SQL using rpc (raw SQL)
                response = supabase.rpc('exec_sql', {'sql': sql}).execute()
                print(f"✅ Command {i} executed successfully")
            except Exception as e:
                print(f"⚠️  Command {i} failed (this might be expected): {e}")
                # Try alternative approach using direct SQL execution
                try:
                    # Use the REST API to execute raw SQL
                    response = supabase.table('students').select('*').limit(1).execute()
                    print(f"✅ Database connection verified")
                except Exception as e2:
                    print(f"❌ Database connection failed: {e2}")
                    return False
        
        # Verify the columns exist
        print("🔍 Verifying schema changes...")
        try:
            # Try to select the new columns
            response = supabase.table('students').select('id, profile_picture, has_profile_picture').limit(1).execute()
            print("✅ Profile picture columns are accessible")
            return True
        except Exception as e:
            print(f"❌ Could not verify columns: {e}")
            print("💡 You may need to run the SQL manually in Supabase SQL Editor")
            return False
        
    except Exception as e:
        print(f"❌ Error updating database schema: {e}")
        return False

def manual_instructions():
    """Print manual instructions for updating the database"""
    print("\n" + "="*60)
    print("📋 MANUAL DATABASE UPDATE REQUIRED")
    print("="*60)
    print("Since the automatic update failed, please follow these steps:")
    print()
    print("1. Go to your Supabase Dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Run the following SQL commands:")
    print()
    print("-- Add profile picture columns")
    print("ALTER TABLE students")
    print("ADD COLUMN IF NOT EXISTS profile_picture TEXT,")
    print("ADD COLUMN IF NOT EXISTS has_profile_picture BOOLEAN DEFAULT FALSE;")
    print()
    print("-- Update existing students")
    print("UPDATE students")
    print("SET has_profile_picture = FALSE")
    print("WHERE has_profile_picture IS NULL;")
    print()
    print("4. After running the SQL, restart your Flask app")
    print("="*60)

if __name__ == '__main__':
    print("🔧 Updating Database Schema for Profile Pictures")
    print("=" * 50)
    
    if update_database_schema():
        print("\n🎉 Database schema updated successfully!")
        print("You can now restart your Flask app and test the profile picture feature.")
    else:
        manual_instructions() 