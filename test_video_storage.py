#!/usr/bin/env python3
"""
Test script to verify video storage system is working correctly.
"""

import os
import sys
import io
from datetime import datetime

# Test configuration
TESTS_PASSED = 0
TESTS_FAILED = 0

def print_test(name, passed, message=""):
    global TESTS_PASSED, TESTS_FAILED
    
    if passed:
        TESTS_PASSED += 1
        print(f"✓ {name}")
        if message:
            print(f"  {message}")
    else:
        TESTS_FAILED += 1
        print(f"✗ {name}")
        if message:
            print(f"  ERROR: {message}")

def test_directories():
    """Test that required directories exist"""
    print("\n=== Testing Directory Structure ===\n")
    
    video_dir = os.path.join(os.path.dirname(__file__), 'uploaded_videos')
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    
    # Check if directories exist (they should be created by app.py)
    video_exists = os.path.exists(video_dir)
    log_exists = os.path.exists(log_dir)
    
    print_test(
        "Video storage directory exists",
        video_exists,
        f"Path: {video_dir}"
    )
    
    print_test(
        "Logs directory exists",
        log_exists,
        f"Path: {log_dir}"
    )
    
    # Test write permissions
    if video_exists:
        test_file = os.path.join(video_dir, '.test_write')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print_test("Video directory is writable", True)
        except Exception as e:
            print_test("Video directory is writable", False, str(e))

def test_imports():
    """Test that app.py can be imported and has required functions"""
    print("\n=== Testing Imports and Functions ===\n")
    
    try:
        from app import (
            save_video_locally,
            upload_video_to_drive,
            VIDEO_STORAGE_DIR,
            LOG_DIR,
            logger
        )
        print_test("Import app.py modules", True)
        
        # Check if functions exist
        print_test(
            "save_video_locally function exists",
            callable(save_video_locally)
        )
        print_test(
            "upload_video_to_drive function exists",
            callable(upload_video_to_drive)
        )
        print_test(
            "VIDEO_STORAGE_DIR defined",
            VIDEO_STORAGE_DIR is not None,
            f"Path: {VIDEO_STORAGE_DIR}"
        )
        print_test(
            "LOG_DIR defined",
            LOG_DIR is not None,
            f"Path: {LOG_DIR}"
        )
        print_test(
            "Logger configured",
            logger is not None
        )
        
    except ImportError as e:
        print_test("Import app.py modules", False, str(e))
    except Exception as e:
        print_test("Import app.py modules", False, str(e))

def test_save_video_locally():
    """Test the save_video_locally function"""
    print("\n=== Testing Local Video Save ===\n")
    
    try:
        from app import save_video_locally, VIDEO_STORAGE_DIR
        
        # Create test video data
        test_content = b"This is a test video file content"
        test_filename = "test_video.mp4"
        
        # Save video
        success, local_path, error = save_video_locally(test_content, test_filename)
        
        print_test(
            "save_video_locally returns success",
            success,
            error if not success else f"Saved to: {local_path}"
        )
        
        if success and local_path:
            # Verify file exists
            file_exists = os.path.exists(local_path)
            print_test(
                "Video file was created",
                file_exists,
                f"Path: {local_path}"
            )
            
            if file_exists:
                # Verify content
                with open(local_path, 'rb') as f:
                    saved_content = f.read()
                
                content_matches = saved_content == test_content
                print_test(
                    "Video content matches original",
                    content_matches,
                    f"Size: {len(saved_content)} bytes"
                )
                
                # Verify filename has timestamp
                basename = os.path.basename(local_path)
                has_timestamp = any(char.isdigit() for char in basename[:8])
                print_test(
                    "Filename includes timestamp",
                    has_timestamp,
                    f"Filename: {basename}"
                )
                
                # Clean up test file
                try:
                    os.remove(local_path)
                    print_test("Test file cleanup", True, "Test file removed")
                except Exception as e:
                    print_test("Test file cleanup", False, str(e))
        
    except Exception as e:
        print_test("Test save_video_locally", False, str(e))

def test_gitignore():
    """Test that .gitignore is properly configured"""
    print("\n=== Testing .gitignore Configuration ===\n")
    
    gitignore_path = os.path.join(os.path.dirname(__file__), '..', '.gitignore')
    
    if not os.path.exists(gitignore_path):
        print_test(".gitignore file exists", False, "File not found")
        return
    
    print_test(".gitignore file exists", True)
    
    with open(gitignore_path, 'r') as f:
        content = f.read()
    
    # Check for required entries
    has_video_dir = 'uploaded_videos' in content
    has_logs_dir = 'backend/logs' in content or 'logs/' in content
    has_video_extensions = '.mp4' in content
    
    print_test(
        ".gitignore includes uploaded_videos directory",
        has_video_dir
    )
    print_test(
        ".gitignore includes logs directory",
        has_logs_dir
    )
    print_test(
        ".gitignore includes video file extensions",
        has_video_extensions
    )

def test_api_endpoints():
    """Test that API endpoints are defined"""
    print("\n=== Testing API Endpoints ===\n")
    
    try:
        from app import app
        
        # Get all routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(str(rule))
        
        # Check for video-related endpoints
        endpoints = {
            '/api/upload-video': '/api/upload-video' in routes,
            '/api/videos/list': '/api/videos/list' in routes,
            '/api/videos/storage-stats': '/api/videos/storage-stats' in routes,
            '/api/video-info/<filename>': any('video-info' in r for r in routes),
        }
        
        for endpoint, exists in endpoints.items():
            print_test(f"Endpoint {endpoint} defined", exists)
        
    except Exception as e:
        print_test("Test API endpoints", False, str(e))

def test_video_manager_script():
    """Test that video manager script exists and is executable"""
    print("\n=== Testing Video Manager Script ===\n")
    
    script_path = os.path.join(os.path.dirname(__file__), 'video_manager.py')
    
    exists = os.path.exists(script_path)
    print_test("video_manager.py exists", exists, f"Path: {script_path}")
    
    if exists:
        is_executable = os.access(script_path, os.X_OK)
        print_test("video_manager.py is executable", is_executable)
        
        # Check if it has required functions
        try:
            with open(script_path, 'r') as f:
                content = f.read()
            
            functions = [
                'list_videos',
                'get_stats',
                'check_logs',
                'find_video',
                'delete_video',
                'export_manifest',
                'cleanup_old_videos'
            ]
            
            for func in functions:
                has_func = f"def {func}" in content
                print_test(f"video_manager has {func} function", has_func)
        except Exception as e:
            print_test("Check video_manager functions", False, str(e))

def test_documentation():
    """Test that documentation exists"""
    print("\n=== Testing Documentation ===\n")
    
    docs = {
        'VIDEO_STORAGE_GUIDE.md': 'Complete guide',
        'QUICK_VIDEO_GUIDE.md': 'Quick reference'
    }
    
    for doc, description in docs.items():
        doc_path = os.path.join(os.path.dirname(__file__), doc)
        exists = os.path.exists(doc_path)
        print_test(f"{doc} exists ({description})", exists, f"Path: {doc_path}")

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✓ Passed: {TESTS_PASSED}")
    print(f"✗ Failed: {TESTS_FAILED}")
    print(f"Total: {TESTS_PASSED + TESTS_FAILED}")
    
    if TESTS_FAILED == 0:
        print("\n🎉 All tests passed! Video storage system is ready.")
    else:
        print(f"\n⚠️  {TESTS_FAILED} test(s) failed. Please review the errors above.")
    
    print("="*60)

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("VIDEO STORAGE SYSTEM TEST SUITE")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_directories()
    test_imports()
    test_save_video_locally()
    test_gitignore()
    test_api_endpoints()
    test_video_manager_script()
    test_documentation()
    
    print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if TESTS_FAILED == 0 else 1)

if __name__ == '__main__':
    main()


