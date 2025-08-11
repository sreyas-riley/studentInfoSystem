#!/usr/bin/env python3
"""
Script to clear all cached data and restart the application properly
"""

import os
import shutil
import subprocess
import sys

def clear_python_cache():
    """Clear Python cache files"""
    print("🧹 Clearing Python cache...")
    
    # Remove __pycache__ directories
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                cache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(cache_path)
                    print(f"  ✅ Removed: {cache_path}")
                except Exception as e:
                    print(f"  ⚠️  Could not remove {cache_path}: {e}")
    
    # Remove .pyc files
    for root, dirs, files in os.walk('.'):
        for file_name in files:
            if file_name.endswith('.pyc'):
                file_path = os.path.join(root, file_name)
                try:
                    os.remove(file_path)
                    print(f"  ✅ Removed: {file_path}")
                except Exception as e:
                    print(f"  ⚠️  Could not remove {file_path}: {e}")

def clear_flask_session():
    """Clear Flask session data"""
    print("\n🗂️  Clearing Flask session data...")
    
    # Remove any session files
    session_files = [
        'flask_session',
        '.flask_session',
        'session',
        '.session'
    ]
    
    for session_file in session_files:
        if os.path.exists(session_file):
            try:
                if os.path.isdir(session_file):
                    shutil.rmtree(session_file)
                else:
                    os.remove(session_file)
                print(f"  ✅ Removed: {session_file}")
            except Exception as e:
                print(f"  ⚠️  Could not remove {session_file}: {e}")

def check_running_app():
    """Check if the app is currently running"""
    print("\n🔍 Checking for running application...")
    
    try:
        # Check if port 5001 is in use
        result = subprocess.run(['lsof', '-ti:5001'], capture_output=True, text=True)
        if result.stdout.strip():
            print("  ⚠️  Application is running on port 5001")
            print("  💡 Please stop it first (Ctrl+C in the terminal where it's running)")
            return True
        else:
            print("  ✅ No application running on port 5001")
            return False
    except FileNotFoundError:
        print("  ℹ️  Could not check for running application (lsof not available)")
        return False

def restart_application():
    """Restart the application"""
    print("\n🚀 Restarting application...")
    
    if check_running_app():
        print("  ⚠️  Please stop the current application first")
        return False
    
    try:
        print("  📝 Starting: python3 app_supabase.py")
        print("  🌐 Access your app at: http://localhost:5001")
        print("  💡 Press Ctrl+C to stop the application")
        print("\n" + "="*50)
        
        # Start the application
        subprocess.run([sys.executable, 'app_supabase.py'])
        return True
    except KeyboardInterrupt:
        print("\n  ✅ Application stopped by user")
        return True
    except Exception as e:
        print(f"  ❌ Error starting application: {e}")
        return False

def main():
    """Main function"""
    print("🔄 Clear Cache and Restart Application")
    print("=" * 50)
    
    # Clear Python cache
    clear_python_cache()
    
    # Clear Flask session
    clear_flask_session()
    
    print("\n✅ Cache cleared successfully!")
    
    # Ask user if they want to restart
    print("\nWould you like to restart the application now? (y/n): ", end='')
    response = input().lower().strip()
    
    if response == 'y':
        restart_application()
    else:
        print("\n🎯 To restart manually, run:")
        print("   python3 app_supabase.py")
        print("\n💡 Remember to:")
        print("   1. Clear browser cache if using web interface")
        print("   2. Use hard refresh (Ctrl+F5 or Cmd+Shift+R)")
        print("   3. Check that your app now shows current database state")

if __name__ == '__main__':
    main() 