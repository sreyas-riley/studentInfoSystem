#!/usr/bin/env python3
"""
Test script for AI-powered attendance verification
"""

import base64
import io
from PIL import Image
import numpy as np

def create_test_image(width=300, height=400, color=(255, 200, 150)):
    """Create a test image for testing AI verification"""
    # Create a simple test image
    img = Image.new('RGB', (width, height), color)
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    img_data = buffer.getvalue()
    return base64.b64encode(img_data).decode('utf-8')

def test_ai_verification():
    """Test the AI verification functions"""
    print("🧪 Testing AI Attendance Verification System")
    print("=" * 50)
    
    # Test 1: Create a test image
    print("\n1. Creating test image...")
    test_image = create_test_image()
    print(f"✅ Test image created (base64 length: {len(test_image)})")
    
    # Test 2: Test data URL prefix stripping
    print("\n2. Testing data URL prefix stripping...")
    try:
        from app_supabase import _strip_data_url_prefix
        test_data_url = f"data:image/jpeg;base64,{test_image}"
        stripped = _strip_data_url_prefix(test_data_url)
        assert stripped == test_image
        print("✅ Data URL prefix stripping works correctly")
    except Exception as e:
        print(f"❌ Data URL prefix stripping failed: {e}")
    
    # Test 3: Test enhanced image verification
    print("\n3. Testing enhanced image verification...")
    try:
        from app_supabase import _enhanced_image_verification
        result = _enhanced_image_verification(test_image, 123)
        print(f"✅ Enhanced verification result: {result}")
    except Exception as e:
        print(f"❌ Enhanced verification failed: {e}")
    
    # Test 4: Test face recognition (if available)
    print("\n4. Testing face recognition...")
    try:
        from app_supabase import _faces_match
        # Test with same image (should match)
        match_result = _faces_match(test_image, test_image)
        print(f"✅ Face recognition test: {match_result}")
    except Exception as e:
        print(f"⚠️  Face recognition not available: {e}")
    
    # Test 5: Test AI verification pipeline
    print("\n5. Testing AI verification pipeline...")
    try:
        # Test the enhanced verification directly since it's the main fallback
        from app_supabase import _enhanced_image_verification
        result = _enhanced_image_verification(test_image, 123)
        print(f"✅ AI verification pipeline result: {result}")
    except Exception as e:
        print(f"❌ AI verification pipeline failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 AI Attendance Verification Test Complete!")
    print("\nTo use the AI attendance system:")
    print("1. Install required packages: pip install -r requirements.txt")
    print("2. Students should upload profile pictures first")
    print("3. When students upload attendance images, AI will automatically verify them")
    print("4. If AI verification succeeds, attendance is marked automatically")
    print("5. If AI verification fails, teachers can still manually verify")

if __name__ == "__main__":
    test_ai_verification() 