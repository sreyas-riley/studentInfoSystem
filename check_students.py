#!/usr/bin/env python3
"""
Script to check the current state of students table
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def check_students_table():
    """Check the current state of students table"""
    try:
        # Get environment variables
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials in .env file")
            return False
        
        print("🔗 Connecting to Supabase...")
        supabase: Client = create_client(supabase_url, supabase_key)
        
        print("\n📊 Students Table Analysis:")
        print("=" * 50)
        
        # Get ALL students (including deleted ones)
        print("\n👥 All Students (including deleted):")
        try:
            all_students_response = supabase.table('students').select('*').execute()
            print(f"  • Total students in database: {len(all_students_response.data)}")
            
            if all_students_response.data:
                for student in all_students_response.data:
                    deleted_status = "❌ DELETED" if student.get('is_deleted') else "✅ ACTIVE"
                    print(f"    - {student['name']} (Roll: {student['roll']}, Class: {student['class']}) - {deleted_status}")
                    if student.get('is_deleted'):
                        print(f"      Deleted by: {student.get('deleted_by')} at {student.get('deleted_at')}")
            else:
                print("    No students found in database")
        except Exception as e:
            print(f"  ❌ Error accessing all students: {e}")
        
        # Get only active students
        print("\n✅ Active Students (not deleted):")
        try:
            active_students_response = supabase.table('students').select('*').eq('is_deleted', False).execute()
            print(f"  • Active students: {len(active_students_response.data)}")
            
            if active_students_response.data:
                for student in active_students_response.data:
                    print(f"    - {student['name']} (Roll: {student['roll']}, Class: {student['class']})")
            else:
                print("    No active students found")
        except Exception as e:
            print(f"  ❌ Error accessing active students: {e}")
        
        # Get only deleted students
        print("\n🗑️  Deleted Students:")
        try:
            deleted_students_response = supabase.table('students').select('*').eq('is_deleted', True).execute()
            print(f"  • Deleted students: {len(deleted_students_response.data)}")
            
            if deleted_students_response.data:
                for student in deleted_students_response.data:
                    print(f"    - {student['name']} (Roll: {student['roll']}, Class: {student['class']})")
                    print(f"      Deleted by: {student.get('deleted_by')} at {student.get('deleted_at')}")
            else:
                print("    No deleted students found")
        except Exception as e:
            print(f"  ❌ Error accessing deleted students: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("🔍 Check Students Table State")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        return
    
    # Check students table
    if check_students_table():
        print("\n✅ Students table analysis completed!")
        print("\n💡 If you see deleted students, they are still in the database but marked as deleted.")
        print("   This is called 'soft delete' - the data is preserved but hidden from normal views.")
    else:
        print("\n❌ Failed to analyze students table")

if __name__ == '__main__':
    main() 