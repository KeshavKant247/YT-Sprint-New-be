#!/usr/bin/env python3
"""
Test script for YouTube download functionality
"""

import os
import sys
import requests
import json

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')

# Test YouTube URLs (use public, short videos)
TEST_URLS = [
    # YouTube Shorts format
    'https://youtube.com/shorts/dQw4w9WgXcQ',
    # Regular YouTube format
    'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    # Short URL format
    'https://youtu.be/dQw4w9WgXcQ',
]

def test_youtube_download(youtube_url, upload_to_drive=False):
    """Test downloading a YouTube video"""
    print(f"\n{'='*70}")
    print(f"Testing YouTube Download")
    print(f"{'='*70}")
    print(f"URL: {youtube_url}")
    print(f"Upload to Drive: {upload_to_drive}")
    print()
    
    try:
        # Make API request
        response = requests.post(
            f'{API_BASE_URL}/api/download-youtube',
            json={
                'youtube_url': youtube_url,
                'content_type': 'Test_Video',
                'upload_to_drive': upload_to_drive
            },
            timeout=300  # 5 minute timeout for large videos
        )
        
        print(f"Status Code: {response.status_code}")
        
        # Parse response
        result = response.json()
        
        if result.get('success'):
            print("\n✅ SUCCESS!")
            print(f"\nDownload Details:")
            print(f"  Filename: {result.get('filename')}")
            print(f"  Local Path: {result.get('local_path')}")
            print(f"  File Size: {result.get('file_size_mb')} MB")
            
            video_info = result.get('video_info', {})
            if video_info:
                print(f"\nVideo Information:")
                print(f"  Title: {video_info.get('title')}")
                print(f"  Duration: {video_info.get('duration')} seconds")
                print(f"  Uploader: {video_info.get('uploader')}")
                print(f"  Upload Date: {video_info.get('upload_date')}")
                print(f"  Views: {video_info.get('view_count', 0):,}")
            
            if result.get('drive_link'):
                print(f"\nGoogle Drive:")
                print(f"  Link: {result.get('drive_link')}")
                print(f"  File ID: {result.get('video_id')}")
            elif result.get('drive_upload_error'):
                print(f"\n⚠️ Drive Upload Failed: {result.get('drive_upload_error')}")
            
            # Verify file exists locally
            local_path = result.get('local_path')
            if local_path and os.path.exists(local_path):
                file_size = os.path.getsize(local_path)
                print(f"\n✓ Verified: File exists locally ({file_size:,} bytes)")
            else:
                print(f"\n❌ Warning: Local file not found at {local_path}")
            
            return True
        else:
            print("\n❌ FAILED!")
            print(f"Error: {result.get('error')}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out (video might be too large or network is slow)")
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Could not connect to API at {API_BASE_URL}")
        print("Make sure the backend server is running:")
        print("  cd backend && python app.py")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_invalid_url():
    """Test with invalid URL"""
    print(f"\n{'='*70}")
    print(f"Testing Invalid URL (Should Fail)")
    print(f"{'='*70}")
    
    try:
        response = requests.post(
            f'{API_BASE_URL}/api/download-youtube',
            json={
                'youtube_url': 'https://not-youtube.com/video',
                'content_type': 'Test_Video',
                'upload_to_drive': False
            },
            timeout=30
        )
        
        result = response.json()
        
        if not result.get('success'):
            print("✅ Correctly rejected invalid URL")
            print(f"Error message: {result.get('error')}")
            return True
        else:
            print("❌ Should have rejected invalid URL")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_url_extraction():
    """Test URL extraction function"""
    print(f"\n{'='*70}")
    print(f"Testing URL Extraction")
    print(f"{'='*70}")
    
    test_cases = [
        ('https://youtube.com/shorts/abc123def45', 'abc123def45'),
        ('https://www.youtube.com/watch?v=abc123def45', 'abc123def45'),
        ('https://youtu.be/abc123def45', 'abc123def45'),
        ('abc123def45', 'abc123def45'),
        ('https://not-youtube.com/video', None),
    ]
    
    all_passed = True
    for url, expected_id in test_cases:
        # Import the extraction function
        from app import extract_youtube_video_id
        
        result_id = extract_youtube_video_id(url)
        passed = result_id == expected_id
        
        status = "✅" if passed else "❌"
        print(f"{status} URL: {url[:50]}")
        print(f"   Expected: {expected_id}, Got: {result_id}")
        
        if not passed:
            all_passed = False
    
    return all_passed

def check_server():
    """Check if backend server is running"""
    try:
        response = requests.get(f'{API_BASE_URL}/health', timeout=5)
        if response.status_code == 200:
            print(f"✅ Backend server is running at {API_BASE_URL}")
            return True
    except:
        pass
    
    print(f"❌ Backend server is not running at {API_BASE_URL}")
    print("\nTo start the server:")
    print("  cd backend")
    print("  python app.py")
    return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print(f"\n{'='*70}")
    print(f"Checking Dependencies")
    print(f"{'='*70}")
    
    try:
        import yt_dlp
        print(f"✅ yt-dlp is installed (version: {yt_dlp.version.__version__})")
        return True
    except ImportError:
        print("❌ yt-dlp is not installed")
        print("\nTo install:")
        print("  pip install yt-dlp")
        return False

def main():
    """Run all tests"""
    print(f"\n{'='*70}")
    print(f"YouTube Download Feature - Test Suite")
    print(f"{'='*70}")
    
    # Check dependencies
    if not check_dependencies():
        print("\n⚠️ Please install missing dependencies first")
        return
    
    # Check server
    if not check_server():
        print("\n⚠️ Please start the backend server first")
        return
    
    # Run tests
    results = []
    
    # Test 1: URL extraction
    print("\n\n=== TEST 1: URL Extraction ===")
    results.append(('URL Extraction', test_url_extraction()))
    
    # Test 2: Invalid URL
    print("\n\n=== TEST 2: Invalid URL Handling ===")
    results.append(('Invalid URL', test_invalid_url()))
    
    # Test 3: Download without Drive upload
    print("\n\n=== TEST 3: Download Video (Local Only) ===")
    print("Note: Using a short test video. This may take 10-30 seconds.")
    print("If you don't have a specific test video, you can skip this test.")
    
    skip = input("\nSkip actual video download test? (y/n): ").lower().strip()
    if skip != 'y':
        # Use a very short video ID for testing
        # Replace with your own test video URL
        test_url = input("Enter a YouTube URL to test (or press Enter to skip): ").strip()
        if test_url:
            results.append(('Download Video', test_youtube_download(test_url, upload_to_drive=False)))
        else:
            print("Skipped video download test")
    else:
        print("Skipped video download test")
    
    # Print summary
    print(f"\n\n{'='*70}")
    print(f"Test Summary")
    print(f"{'='*70}")
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")

if __name__ == '__main__':
    main()


