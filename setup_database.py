#!/usr/bin/env python3
"""
Database setup script for Student Info App
This script will help you set up the database tables in Supabase
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_setup_instructions():
    """Print step-by-step setup instructions"""
    print("🗄️  Supabase Database Setup Instructions")
    print("=" * 60)
    print()
    print("📋 Step 1: Access Your Supabase Dashboard")
    print("   • Go to: https://supabase.com/dashboard")
    print("   • Sign in to your account")
    print("   • Select your project: ywcomtwiavpglsbncftn")
    print()
    print("📋 Step 2: Open SQL Editor")
    print("   • In your Supabase dashboard, click on 'SQL Editor' in the left sidebar")
    print("   • Click 'New query' to create a new SQL query")
    print()
    print("📋 Step 3: Run the Setup Script")
    print("   • Copy the entire contents of 'supabase_setup.sql'")
    print("   • Paste it into the SQL Editor")
    print("   • Click 'Run' to execute the script")
    print()
    print("📋 Step 4: Verify Setup")
    print("   • Go to 'Table Editor' in the left sidebar")
    print("   • You should see these tables created:")
    print("     ✅ users")
    print("     ✅ students") 
    print("     ✅ data_log")
    print("     ✅ attendance")
    print("     ✅ clear_log")
    print()
    print("📋 Step 5: Test Connection")
    print("   • Run: python3 test_connection.py")
    print("   • You should see 'All tests passed!'")
    print()
    print("📋 Step 6: Start the Application")
    print("   • Run: python3 app_supabase.py")
    print("   • Access at: http://localhost:5001")
    print()
    print("🔐 Default Login Credentials:")
    print("   • Principal: username='principal', password='principal123'")
    print("   • Teachers: username='teacher_1' to 'teacher_12', password='teacher123'")
    print("   • General Teacher: username='teacher', password='teacher123'")
    print()

def show_sql_script():
    """Show the SQL script that needs to be run"""
    print("📄 SQL Script to Run in Supabase:")
    print("=" * 60)
    print()
    
    try:
        with open('supabase_setup.sql', 'r') as f:
            sql_content = f.read()
        print(sql_content)
    except FileNotFoundError:
        print("❌ supabase_setup.sql file not found!")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 Student Info App - Database Setup")
    print("=" * 60)
    print()
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please run the setup first: python3 setup.py")
        return
    
    # Check Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
        return
    
    print(f"✅ Supabase URL: {supabase_url}")
    print(f"✅ Supabase Key: {supabase_key[:20]}...")
    print()
    
    # Print instructions
    print_setup_instructions()
    
    # Ask if user wants to see the SQL script
    print("Would you like to see the SQL script that needs to be run? (y/n): ", end='')
    response = input().lower().strip()
    
    if response == 'y':
        show_sql_script()
    
    print("\n🎯 Next Steps:")
    print("1. Follow the instructions above to set up your database")
    print("2. Run: python3 test_connection.py to verify setup")
    print("3. Run: python3 app_supabase.py to start the application")
    print()
    print("💡 Need help? Check README_SUPABASE.md for detailed instructions")

if __name__ == '__main__':
    main() 