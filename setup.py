#!/usr/bin/env python3
"""
Setup script for Student Info App with Supabase
This script helps you configure your environment variables and set up the database.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with Supabase credentials"""
    env_path = Path('.env')
    
    if env_path.exists():
        print("⚠️  .env file already exists. Do you want to overwrite it? (y/n): ", end='')
        response = input().lower().strip()
        if response != 'y':
            print("Setup cancelled.")
            return False
    
    print("\n🔧 Setting up Supabase configuration...")
    print("=" * 50)
    
    # Get Supabase URL
    supabase_url = input("Enter your Supabase URL (e.g., https://your-project.supabase.co): ").strip()
    if not supabase_url:
        print("❌ Supabase URL is required!")
        return False
    
    # Get Supabase anon key
    supabase_key = input("Enter your Supabase anon key: ").strip()
    if not supabase_key:
        print("❌ Supabase anon key is required!")
        return False
    
    # Generate Flask secret key
    import secrets
    flask_secret = secrets.token_hex(32)
    
    # Create .env file content
    env_content = f"""# Supabase Configuration
SUPABASE_URL={supabase_url}
SUPABASE_KEY={supabase_key}

# Flask Configuration
FLASK_SECRET_KEY={flask_secret}
FLASK_ENV=development
"""
    
    # Write .env file
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'flask',
        'flask-cors',
        'supabase',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install them using: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def setup_database():
    """Provide instructions for database setup"""
    print("\n🗄️  Database Setup Instructions")
    print("=" * 50)
    print("1. Go to your Supabase dashboard: https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Go to the SQL Editor")
    print("4. Copy and paste the contents of 'supabase_setup.sql'")
    print("5. Run the SQL script")
    print("6. Verify that the following tables were created:")
    print("   - users")
    print("   - students")
    print("   - data_log")
    print("   - attendance")
    print("   - clear_log")
    print("\nThe SQL script will also:")
    print("- Insert default teachers and principal accounts")
    print("- Create indexes for better performance")
    print("- Enable Row Level Security (RLS)")
    print("- Set up basic RLS policies")

def main():
    """Main setup function"""
    print("🚀 Student Info App - Supabase Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('app_supabase.py').exists():
        print("❌ Please run this script from the student_info_app directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\n💡 Install missing dependencies first:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Database setup instructions
    setup_database()
    
    print("\n🎉 Setup completed!")
    print("=" * 50)
    print("Next steps:")
    print("1. Set up your Supabase database using the SQL script")
    print("2. Run the application: python app_supabase.py")
    print("3. Access the app at: http://localhost:5001")
    print("\nDefault login credentials:")
    print("- Principal: username='principal', password='principal123'")
    print("- Teachers: username='teacher_1' to 'teacher_12', password='teacher123'")
    print("- General teacher: username='teacher', password='teacher123'")

if __name__ == '__main__':
    main() 