#!/usr/bin/env python3
"""
Script to refresh data from Supabase and clear any cached information
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json

# Load environment variables
load_dotenv()

def refresh_database_data():
    """Refresh all data from Supabase database"""
    try:
        # Get environment variables
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials in .env file")
            return False
        
        print("🔗 Connecting to Supabase...")
        supabase: Client = create_client(supabase_url, supabase_key)
        
        print("\n📊 Current Database State:")
        print("=" * 40)
        
        # Check users table
        print("\n👥 Users Table:")
        try:
            users_response = supabase.table('users').select('*').execute()
            print(f"  • Total users: {len(users_response.data)}")
            for user in users_response.data:
                print(f"    - {user['username']} ({user['role']}) - Class: {user['class'] or 'N/A'}")
        except Exception as e:
            print(f"  ❌ Error accessing users: {e}")
        
        # Check students table
        print("\n🎓 Students Table:")
        try:
            students_response = supabase.table('students').select('*').execute()
            print(f"  • Total students: {len(students_response.data)}")
            for student in students_response.data:
                print(f"    - {student['name']} (Roll: {student['roll']}, Class: {student['class']})")
        except Exception as e:
            print(f"  ❌ Error accessing students: {e}")
        
        # Check data_log table
        print("\n📝 Data Log Table:")
        try:
            log_response = supabase.table('data_log').select('*').execute()
            print(f"  • Total log entries: {len(log_response.data)}")
        except Exception as e:
            print(f"  ❌ Error accessing data_log: {e}")
        
        # Check attendance table
        print("\n📅 Attendance Table:")
        try:
            attendance_response = supabase.table('attendance').select('*').execute()
            print(f"  • Total attendance records: {len(attendance_response.data)}")
        except Exception as e:
            print(f"  ❌ Error accessing attendance: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def clear_browser_cache_instructions():
    """Provide instructions to clear browser cache"""
    print("\n🌐 Browser Cache Clearing Instructions:")
    print("=" * 50)
    print("If you're still seeing old data in your browser:")
    print()
    print("1. **Hard Refresh**: Press Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)")
    print("2. **Clear Browser Cache**:")
    print("   • Chrome: Settings > Privacy > Clear browsing data")
    print("   • Firefox: Options > Privacy > Clear Data")
    print("   • Safari: Preferences > Privacy > Manage Website Data")
    print("3. **Open in Incognito/Private Mode**: This bypasses cache")
    print("4. **Clear Local Storage**: Open DevTools (F12) > Application > Storage > Clear")

def restart_application_instructions():
    """Provide instructions to restart the application"""
    print("\n🔄 Application Restart Instructions:")
    print("=" * 40)
    print("To ensure your app picks up the latest data:")
    print()
    print("1. **Stop the current application**: Press Ctrl+C in the terminal")
    print("2. **Restart the application**:")
    print("   python3 app_supabase.py")
    print("3. **Clear any cached data**: The app will fetch fresh data from Supabase")

def insert_default_users_if_needed():
    """Insert default users if the database is empty"""
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Check if users table is empty
        users_response = supabase.table('users').select('*').execute()
        
        if len(users_response.data) == 0:
            print("\n⚠️  No users found in database!")
            print("Would you like to insert the default users? (y/n): ", end='')
            response = input().lower().strip()
            
            if response == 'y':
                print("\n📝 Inserting default users...")
                
                # Default users to insert
                default_users = [
                    {'username': 'teacher', 'password': 'teacher123', 'role': 'teacher', 'class': None},
                    {'username': 'teacher_k', 'password': 'teacher123', 'role': 'teacher', 'class': 'K'},
                    {'username': 'teacher_1', 'password': 'teacher123', 'role': 'teacher', 'class': '1'},
                    {'username': 'teacher_2', 'password': 'teacher123', 'role': 'teacher', 'class': '2'},
                    {'username': 'teacher_3', 'password': 'teacher123', 'role': 'teacher', 'class': '3'},
                    {'username': 'teacher_4', 'password': 'teacher123', 'role': 'teacher', 'class': '4'},
                    {'username': 'teacher_5', 'password': 'teacher123', 'role': 'teacher', 'class': '5'},
                    {'username': 'teacher_6', 'password': 'teacher123', 'role': 'teacher', 'class': '6'},
                    {'username': 'teacher_7', 'password': 'teacher123', 'role': 'teacher', 'class': '7'},
                    {'username': 'teacher_8', 'password': 'teacher123', 'role': 'teacher', 'class': '8'},
                    {'username': 'teacher_9', 'password': 'teacher123', 'role': 'teacher', 'class': '9'},
                    {'username': 'teacher_10', 'password': 'teacher123', 'role': 'teacher', 'class': '10'},
                    {'username': 'teacher_11', 'password': 'teacher123', 'role': 'teacher', 'class': '11'},
                    {'username': 'teacher_12', 'password': 'teacher123', 'role': 'teacher', 'class': '12'},
                    {'username': 'principal', 'password': 'principal123', 'role': 'principal', 'class': None}
                ]
                
                inserted_count = 0
                for user in default_users:
                    try:
                        response = supabase.table('users').insert(user).execute()
                        if response.data:
                            print(f"  ✅ Inserted: {user['username']}")
                            inserted_count += 1
                    except Exception as e:
                        print(f"  ❌ Error inserting {user['username']}: {e}")
                
                print(f"\n🎉 Successfully inserted {inserted_count} users!")
            else:
                print("Skipping user insertion.")
        
    except Exception as e:
        print(f"❌ Error checking/inserting users: {e}")

def main():
    """Main function"""
    print("🔄 Refresh Data from Supabase")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        return
    
    # Refresh database data
    if refresh_database_data():
        print("\n✅ Database data refreshed successfully!")
        
        # Check if users need to be inserted
        insert_default_users_if_needed()
        
        # Provide instructions
        clear_browser_cache_instructions()
        restart_application_instructions()
        
        print("\n🎯 Next Steps:")
        print("1. Clear your browser cache (if using web interface)")
        print("2. Restart your application: python3 app_supabase.py")
        print("3. The app will now show the current data from Supabase")
        
    else:
        print("\n❌ Failed to refresh database data")

if __name__ == '__main__':
    main() 