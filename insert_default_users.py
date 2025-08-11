#!/usr/bin/env python3
"""
Script to insert default users (teachers and principal) into Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def insert_default_users():
    """Insert default users into the database"""
    try:
        # Get environment variables
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials in .env file")
            return False
        
        print("🔗 Connecting to Supabase...")
        supabase: Client = create_client(supabase_url, supabase_key)
        
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
        
        print(f"📝 Inserting {len(default_users)} default users...")
        
        # Insert users one by one to handle any conflicts
        inserted_count = 0
        for user in default_users:
            try:
                response = supabase.table('users').insert(user).execute()
                if response.data:
                    print(f"✅ Inserted: {user['username']} ({user['role']})")
                    inserted_count += 1
                else:
                    print(f"⚠️  User {user['username']} might already exist")
            except Exception as e:
                if "duplicate key" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"⚠️  User {user['username']} already exists")
                else:
                    print(f"❌ Error inserting {user['username']}: {e}")
        
        print(f"\n🎉 Successfully inserted {inserted_count} users!")
        
        # Verify the insertion
        print("\n📊 Verifying users in database...")
        response = supabase.table('users').select('*').execute()
        print(f"Total users in database: {len(response.data)}")
        
        # Show the users
        for user in response.data:
            print(f"  • {user['username']} ({user['role']}) - Class: {user['class'] or 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_rls_policies():
    """Check if RLS policies might be blocking access"""
    print("\n🔍 RLS Policy Check:")
    print("If you can't see users in the Supabase dashboard, it might be due to RLS policies.")
    print("The RLS policies in supabase_setup.sql might be too restrictive.")
    print("\n💡 Solution: You can temporarily disable RLS to see the data:")
    print("1. Go to your Supabase dashboard")
    print("2. Navigate to Authentication > Policies")
    print("3. Find the 'users' table")
    print("4. Click 'Disable RLS' temporarily")
    print("5. Check your data")
    print("6. Re-enable RLS when done")

def main():
    """Main function"""
    print("👥 Insert Default Users into Supabase")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        return
    
    # Insert default users
    if insert_default_users():
        print("\n✅ Default users have been inserted successfully!")
        print("\n🔐 You can now login with:")
        print("  • Principal: username='principal', password='principal123'")
        print("  • Teachers: username='teacher_1' to 'teacher_12', password='teacher123'")
        print("  • General Teacher: username='teacher', password='teacher123'")
    else:
        print("\n❌ Failed to insert default users")
        check_rls_policies()

if __name__ == '__main__':
    main() 