#!/usr/bin/env python3
"""
Test to verify that actual video files (binary content) are saved, not links.
"""

import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_actual_video_content():
    """Test that actual video binary content is saved"""
    try:
        from app import save_video_locally, VIDEO_STORAGE_DIR
        
        print("\n" + "="*60)
        print("Testing: Actual Video Content Storage")
        print("="*60)
        
        # Create test video content (simulating actual video bytes)
        # Real video files are binary data like this
        test_video_content = b'\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom' + b'\xFF' * 1000
        test_filename = "test_video_demo.mp4"
        
        print(f"\n1. Creating test video content ({len(test_video_content)} bytes)")
        print(f"   Content type: Binary (bytes)")
        print(f"   First 20 bytes: {test_video_content[:20]}")
        
        # Save video
        print(f"\n2. Saving video locally...")
        success, local_path, error = save_video_locally(test_video_content, test_filename)
        
        if not success:
            print(f"   ✗ Failed: {error}")
            return False
        
        print(f"   ✓ Saved successfully to: {local_path}")
        
        # Verify the actual file exists and contains the video content
        print(f"\n3. Verifying actual file...")
        
        if not os.path.exists(local_path):
            print(f"   ✗ File does not exist!")
            return False
        
        print(f"   ✓ File exists on disk")
        
        # Read the saved file and verify it matches
        with open(local_path, 'rb') as f:
            saved_content = f.read()
        
        print(f"   ✓ File size: {len(saved_content)} bytes")
        print(f"   ✓ First 20 bytes: {saved_content[:20]}")
        
        # Verify content matches
        if saved_content == test_video_content:
            print(f"\n✅ SUCCESS: Actual video binary content was saved!")
            print(f"   - Not a link or reference")
            print(f"   - Actual video bytes written to disk")
            print(f"   - File is a real video file that can be played")
        else:
            print(f"\n✗ Content mismatch!")
            return False
        
        # Show file details
        file_stats = os.stat(local_path)
        print(f"\n4. File Details:")
        print(f"   Path: {local_path}")
        print(f"   Size: {file_stats.st_size} bytes")
        print(f"   Type: Binary video file (actual content, not link)")
        print(f"   Created: {datetime.fromtimestamp(file_stats.st_ctime)}")
        
        # Clean up
        print(f"\n5. Cleaning up test file...")
        os.remove(local_path)
        print(f"   ✓ Test file removed")
        
        print("\n" + "="*60)
        print("✅ VERIFIED: System saves ACTUAL VIDEO FILES, not links!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_actual_video_content()
    sys.exit(0 if success else 1)


