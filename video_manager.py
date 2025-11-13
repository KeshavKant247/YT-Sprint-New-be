#!/usr/bin/env python3
"""
Video Storage Manager Utility

This script provides command-line utilities for managing locally stored videos.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import json

# Add parent directory to path to import from app.py
sys.path.insert(0, os.path.dirname(__file__))

VIDEO_STORAGE_DIR = os.path.join(os.path.dirname(__file__), 'uploaded_videos')
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')

def ensure_directories():
    """Ensure storage directories exist"""
    os.makedirs(VIDEO_STORAGE_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    print(f"✓ Directories verified")
    print(f"  - Videos: {VIDEO_STORAGE_DIR}")
    print(f"  - Logs: {LOG_DIR}")

def list_videos():
    """List all stored videos"""
    if not os.path.exists(VIDEO_STORAGE_DIR):
        print("❌ Video storage directory does not exist")
        return
    
    videos = []
    total_size = 0
    
    for filename in os.listdir(VIDEO_STORAGE_DIR):
        filepath = os.path.join(VIDEO_STORAGE_DIR, filename)
        
        if os.path.isfile(filepath) and not filename.startswith('.'):
            stats = os.stat(filepath)
            size_mb = stats.st_size / (1024 * 1024)
            created = datetime.fromtimestamp(stats.st_ctime)
            
            videos.append({
                'filename': filename,
                'size_mb': size_mb,
                'created': created,
                'path': filepath
            })
            total_size += stats.st_size
    
    videos.sort(key=lambda x: x['created'], reverse=True)
    
    print(f"\n📹 Total Videos: {len(videos)}")
    print(f"💾 Total Size: {total_size / (1024 * 1024 * 1024):.2f} GB")
    print("\n" + "="*80)
    
    for i, video in enumerate(videos, 1):
        print(f"\n{i}. {video['filename']}")
        print(f"   Size: {video['size_mb']:.2f} MB")
        print(f"   Created: {video['created'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Path: {video['path']}")

def get_stats():
    """Get storage statistics"""
    if not os.path.exists(VIDEO_STORAGE_DIR):
        print("❌ Video storage directory does not exist")
        return
    
    total_size = 0
    video_count = 0
    file_types = {}
    
    for filename in os.listdir(VIDEO_STORAGE_DIR):
        filepath = os.path.join(VIDEO_STORAGE_DIR, filename)
        
        if os.path.isfile(filepath) and not filename.startswith('.'):
            video_count += 1
            size = os.path.getsize(filepath)
            total_size += size
            
            ext = os.path.splitext(filename)[1].lower()
            file_types[ext] = file_types.get(ext, 0) + 1
    
    print("\n📊 Storage Statistics")
    print("="*50)
    print(f"Total Videos: {video_count}")
    print(f"Total Size: {total_size / (1024 * 1024):.2f} MB ({total_size / (1024 * 1024 * 1024):.2f} GB)")
    print(f"Average Size: {(total_size / video_count / (1024 * 1024)):.2f} MB" if video_count > 0 else "N/A")
    print(f"Storage Path: {VIDEO_STORAGE_DIR}")
    
    if file_types:
        print("\nFile Types:")
        for ext, count in sorted(file_types.items()):
            print(f"  {ext}: {count} files")

def check_logs(lines=50):
    """Display recent log entries"""
    log_file = os.path.join(LOG_DIR, 'video_uploads.log')
    
    if not os.path.exists(log_file):
        print("❌ Log file does not exist")
        return
    
    print(f"\n📋 Last {lines} Log Entries")
    print("="*80)
    
    try:
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            for line in recent_lines:
                print(line.rstrip())
    except Exception as e:
        print(f"❌ Error reading log file: {e}")

def find_video(search_term):
    """Find videos matching search term"""
    if not os.path.exists(VIDEO_STORAGE_DIR):
        print("❌ Video storage directory does not exist")
        return
    
    matches = []
    
    for filename in os.listdir(VIDEO_STORAGE_DIR):
        filepath = os.path.join(VIDEO_STORAGE_DIR, filename)
        
        if os.path.isfile(filepath) and search_term.lower() in filename.lower():
            stats = os.stat(filepath)
            size_mb = stats.st_size / (1024 * 1024)
            created = datetime.fromtimestamp(stats.st_ctime)
            
            matches.append({
                'filename': filename,
                'size_mb': size_mb,
                'created': created,
                'path': filepath
            })
    
    if not matches:
        print(f"\n❌ No videos found matching: {search_term}")
        return
    
    print(f"\n🔍 Found {len(matches)} matching video(s)")
    print("="*80)
    
    for i, video in enumerate(matches, 1):
        print(f"\n{i}. {video['filename']}")
        print(f"   Size: {video['size_mb']:.2f} MB")
        print(f"   Created: {video['created'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Path: {video['path']}")

def delete_video(filename):
    """Delete a specific video file"""
    filepath = os.path.join(VIDEO_STORAGE_DIR, filename)
    
    if not os.path.exists(filepath):
        print(f"❌ Video not found: {filename}")
        return
    
    try:
        size = os.path.getsize(filepath)
        size_mb = size / (1024 * 1024)
        
        confirm = input(f"⚠️  Delete '{filename}' ({size_mb:.2f} MB)? (yes/no): ")
        
        if confirm.lower() == 'yes':
            os.remove(filepath)
            print(f"✓ Deleted: {filename}")
        else:
            print("❌ Deletion cancelled")
    except Exception as e:
        print(f"❌ Error deleting video: {e}")

def export_manifest():
    """Export a JSON manifest of all videos"""
    if not os.path.exists(VIDEO_STORAGE_DIR):
        print("❌ Video storage directory does not exist")
        return
    
    videos = []
    
    for filename in os.listdir(VIDEO_STORAGE_DIR):
        filepath = os.path.join(VIDEO_STORAGE_DIR, filename)
        
        if os.path.isfile(filepath) and not filename.startswith('.'):
            stats = os.stat(filepath)
            
            videos.append({
                'filename': filename,
                'size_bytes': stats.st_size,
                'size_mb': round(stats.st_size / (1024 * 1024), 2),
                'created': datetime.fromtimestamp(stats.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                'path': filepath
            })
    
    manifest_file = os.path.join(LOG_DIR, f'video_manifest_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    
    manifest = {
        'generated': datetime.now().isoformat(),
        'total_videos': len(videos),
        'total_size_bytes': sum(v['size_bytes'] for v in videos),
        'total_size_mb': round(sum(v['size_bytes'] for v in videos) / (1024 * 1024), 2),
        'videos': videos
    }
    
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✓ Manifest exported: {manifest_file}")
    print(f"  Total Videos: {len(videos)}")
    print(f"  Total Size: {manifest['total_size_mb']} MB")

def cleanup_old_videos(days=30, dry_run=True):
    """Clean up videos older than specified days"""
    if not os.path.exists(VIDEO_STORAGE_DIR):
        print("❌ Video storage directory does not exist")
        return
    
    from datetime import timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    old_videos = []
    total_size = 0
    
    for filename in os.listdir(VIDEO_STORAGE_DIR):
        filepath = os.path.join(VIDEO_STORAGE_DIR, filename)
        
        if os.path.isfile(filepath) and not filename.startswith('.'):
            created = datetime.fromtimestamp(os.path.getctime(filepath))
            
            if created < cutoff_date:
                size = os.path.getsize(filepath)
                old_videos.append({
                    'filename': filename,
                    'path': filepath,
                    'size': size,
                    'created': created
                })
                total_size += size
    
    if not old_videos:
        print(f"\n✓ No videos older than {days} days found")
        return
    
    print(f"\n🗑️  Found {len(old_videos)} videos older than {days} days")
    print(f"   Total size: {total_size / (1024 * 1024):.2f} MB")
    print("="*80)
    
    for video in old_videos:
        print(f"\n  - {video['filename']}")
        print(f"    Size: {video['size'] / (1024 * 1024):.2f} MB")
        print(f"    Created: {video['created'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    if dry_run:
        print(f"\n⚠️  DRY RUN MODE - No files deleted")
        print(f"   Run with --execute to actually delete these files")
    else:
        confirm = input(f"\n⚠️  Delete {len(old_videos)} videos? (yes/no): ")
        
        if confirm.lower() == 'yes':
            for video in old_videos:
                try:
                    os.remove(video['path'])
                    print(f"✓ Deleted: {video['filename']}")
                except Exception as e:
                    print(f"❌ Error deleting {video['filename']}: {e}")
        else:
            print("❌ Cleanup cancelled")

def print_help():
    """Print help message"""
    print("""
Video Storage Manager
=====================

Usage: python video_manager.py <command> [options]

Commands:
    list              - List all stored videos
    stats             - Show storage statistics
    logs [lines]      - Show recent log entries (default: 50 lines)
    find <term>       - Find videos matching search term
    delete <filename> - Delete a specific video
    manifest          - Export JSON manifest of all videos
    cleanup <days>    - Show videos older than N days (dry run)
    cleanup-exec <days> - Delete videos older than N days
    check             - Verify directories exist
    help              - Show this help message

Examples:
    python video_manager.py list
    python video_manager.py stats
    python video_manager.py logs 100
    python video_manager.py find "tutorial"
    python video_manager.py delete "20241112_143052_video.mp4"
    python video_manager.py cleanup 30
    python video_manager.py cleanup-exec 30
    """)

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_videos()
    elif command == 'stats':
        get_stats()
    elif command == 'logs':
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        check_logs(lines)
    elif command == 'find':
        if len(sys.argv) < 3:
            print("❌ Usage: python video_manager.py find <search_term>")
            return
        find_video(sys.argv[2])
    elif command == 'delete':
        if len(sys.argv) < 3:
            print("❌ Usage: python video_manager.py delete <filename>")
            return
        delete_video(sys.argv[2])
    elif command == 'manifest':
        export_manifest()
    elif command == 'cleanup':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        cleanup_old_videos(days, dry_run=True)
    elif command == 'cleanup-exec':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        cleanup_old_videos(days, dry_run=False)
    elif command == 'check':
        ensure_directories()
    elif command == 'help':
        print_help()
    else:
        print(f"❌ Unknown command: {command}")
        print_help()

if __name__ == '__main__':
    main()


