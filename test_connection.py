#!/usr/bin/env python3
"""
Test script to verify Supabase connection
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test the Supabase connection"""
    try:
        # Get environment variables
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials in .env file")
            return False
        
        print(f"🔗 Connecting to Supabase...")
        print(f"URL: {supabase_url}")
        print(f"Key: {supabase_key[:20]}...")
        
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Test connection by trying to access a table
        print("📊 Testing database connection...")
        
        # Try to access the users table
        response = supabase.table('users').select('*').limit(1).execute()
        
        print("✅ Successfully connected to Supabase!")
        print(f"📋 Found {len(response.data)} users in database")
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")
        return False

def check_tables():
    """Check if required tables exist"""
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        supabase: Client = create_client(supabase_url, supabase_key)
        
        required_tables = ['users', 'students', 'data_log', 'attendance', 'clear_log']
        
        print("\n📋 Checking required tables...")
        
        for table in required_tables:
            try:
                response = supabase.table(table).select('*').limit(1).execute()
                print(f"✅ {table} table exists")
            except Exception as e:
                print(f"❌ {table} table missing or inaccessible: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Testing Supabase Connection")
    print("=" * 40)
    
    # Test connection
    if test_supabase_connection():
        # Check tables
        check_tables()
        print("\n🎉 All tests passed! Your Supabase connection is working.")
    else:
        print("\n💡 Make sure to:")
        print("1. Set up your Supabase database using supabase_setup.sql")
        print("2. Check your .env file has correct credentials")
        print("3. Verify your Supabase project is active") 