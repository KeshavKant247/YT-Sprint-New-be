# Video Storage System - Complete Guide

## 🎯 Overview

This system ensures **NO VIDEO IS EVER LOST** by implementing a robust two-tier storage approach:

1. **Local Storage (Primary Backup)** - Videos are saved to the backend server FIRST
2. **Google Drive (Cloud Storage)** - Videos are then uploaded to Google Drive

### Key Features

✅ **Atomic Local Storage** - Videos are saved locally before any Drive upload attempts  
✅ **Comprehensive Logging** - Every upload is tracked with detailed logs  
✅ **Error Recovery** - Even if Drive upload fails, the video is safe locally  
✅ **Automatic Directory Creation** - Storage directories are created automatically  
✅ **Timestamped Filenames** - Prevents filename conflicts  
✅ **File Verification** - Ensures files are written correctly  
✅ **Management APIs** - Query video storage statistics and information  

---

## 📁 Directory Structure

```
backend/
├── uploaded_videos/          # All uploaded videos stored here
│   ├── 20241112_143052_ContentType_video.mp4
│   ├── 20241112_143153_Tutorial_lesson.mp4
│   └── ...
├── logs/                     # Upload logs
│   └── video_uploads.log    # Detailed upload history
└── app.py                   # Main application
```

---

## 🔄 Upload Flow

### Step-by-Step Process

```
1. User uploads video via frontend
        ↓
2. Backend receives video file
        ↓
3. [CRITICAL] Save to local storage FIRST
   - Create timestamped filename
   - Write to temp file (.tmp)
   - Verify file integrity
   - Atomic move to final location
   - Log success
        ↓
4. Upload to Google Drive
   - Upload file content
   - Set permissions
   - Get Drive file ID
   - Log success
        ↓
5. Return response with:
   - Drive ID
   - Drive link
   - Local backup path
   - File size
```

### What Happens If Something Fails?

#### Scenario 1: Local Save Fails
- **Response**: Error returned immediately
- **Action Required**: Check disk space and permissions
- **Video Status**: ❌ Not saved (critical error)

#### Scenario 2: Drive Upload Fails
- **Response**: Error returned with local backup path
- **Video Status**: ✅ Safe in local storage
- **Action Required**: Retry Drive upload manually or fix Drive credentials
- **Important**: Video is NOT lost!

#### Scenario 3: Both Succeed
- **Response**: Success with all details
- **Video Status**: ✅✅ Saved locally AND in Drive
- **Action Required**: None

---

## 📊 API Endpoints

### 1. Upload Video
```http
POST /api/upload-video
Content-Type: multipart/form-data

Body:
  video: <file>
  contentType: "Tutorial" (optional)
```

**Success Response:**
```json
{
  "success": true,
  "video_id": "1ABC123...",
  "drive_link": "https://drive.google.com/file/d/1ABC123.../view",
  "filename": "Tutorial_video.mp4",
  "local_backup": "/path/to/uploaded_videos/20241112_143052_Tutorial_video.mp4",
  "file_size_mb": 15.5
}
```

**Failure Response (Drive Failed, Local Succeeded):**
```json
{
  "success": false,
  "error": "Failed to upload to Drive: ...",
  "local_backup": "/path/to/uploaded_videos/20241112_143052_Tutorial_video.mp4",
  "message": "Video saved locally but Drive upload failed. Video is NOT lost."
}
```

### 2. List All Videos
```http
GET /api/videos/list
```

**Response:**
```json
{
  "success": true,
  "videos": [
    {
      "filename": "20241112_143052_Tutorial_video.mp4",
      "size_bytes": 16252928,
      "size_mb": 15.5,
      "created": "2024-11-12T14:30:52",
      "modified": "2024-11-12T14:30:52"
    }
  ],
  "count": 1,
  "total_size_mb": 15.5
}
```

### 3. Get Storage Statistics
```http
GET /api/videos/storage-stats
```

**Response:**
```json
{
  "success": true,
  "video_count": 42,
  "total_size_bytes": 1073741824,
  "total_size_mb": 1024.0,
  "total_size_gb": 1.0,
  "storage_path": "/path/to/uploaded_videos"
}
```

### 4. Get Video Info
```http
GET /api/video-info/<filename>
```

**Response:**
```json
{
  "success": true,
  "filename": "20241112_143052_Tutorial_video.mp4",
  "size_bytes": 16252928,
  "size_mb": 15.5,
  "created": "2024-11-12T14:30:52",
  "modified": "2024-11-12T14:30:52"
}
```

---

## 📝 Logging System

### Log Location
```
backend/logs/video_uploads.log
```

### Log Entries

**Successful Upload:**
```
2024-11-12 14:30:52 - INFO - Received video upload: Tutorial_video.mp4 (15.50 MB, video/mp4)
2024-11-12 14:30:52 - INFO - Video saved locally: 20241112_143052_Tutorial_video.mp4 (16252928 bytes)
2024-11-12 14:30:52 - INFO - Starting Drive upload for: Tutorial_video.mp4
2024-11-12 14:30:55 - INFO - Drive upload successful: Tutorial_video.mp4 (ID: 1ABC123...)
2024-11-12 14:30:55 - INFO - Permissions set for: Tutorial_video.mp4 (ID: 1ABC123...)
2024-11-12 14:30:55 - INFO - ✓ Complete upload success: Tutorial_video.mp4 (Drive ID: 1ABC123..., Local: /path/to/uploaded_videos/20241112_143052_Tutorial_video.mp4)
```

**Drive Upload Failed:**
```
2024-11-12 14:35:12 - INFO - Received video upload: lesson.mp4 (25.30 MB, video/mp4)
2024-11-12 14:35:13 - INFO - Video saved locally: 20241112_143513_lesson.mp4 (26525696 bytes)
2024-11-12 14:35:13 - INFO - Starting Drive upload for: lesson.mp4
2024-11-12 14:35:15 - ERROR - Drive upload failed for lesson.mp4: Could not initialize Drive service
2024-11-12 14:35:15 - INFO - Video backup available at: /path/to/uploaded_videos/20241112_143513_lesson.mp4
2024-11-12 14:35:15 - WARNING - Drive upload failed but video is saved locally: /path/to/uploaded_videos/20241112_143513_lesson.mp4
```

---

## 🛠️ Troubleshooting

### Problem: Videos Not Being Saved Locally

**Check:**
1. Disk space: `df -h`
2. Directory permissions: `ls -la backend/uploaded_videos/`
3. Logs: `cat backend/logs/video_uploads.log`

**Fix:**
```bash
# Create directory if missing
mkdir -p backend/uploaded_videos

# Fix permissions
chmod 755 backend/uploaded_videos
```

### Problem: Drive Upload Failing

**Symptoms:**
- Videos saved locally but not appearing in Drive
- Error logs mention Drive service initialization

**Check:**
1. `credentials.json` exists in backend folder
2. `DRIVE_FOLDER_ID` environment variable is set
3. Service account has access to the Drive folder

**Fix:**
```bash
# Check credentials
ls -la backend/credentials.json

# Check environment variables
cat backend/.env | grep DRIVE_FOLDER_ID

# Test Drive connection
python backend/test_drive_upload.py
```

### Problem: Large Video Upload Times Out

**Solution:**
Increase timeout in your web server configuration:

**Gunicorn:**
```bash
gunicorn --timeout 600 app:app
```

**Nginx:**
```nginx
client_max_body_size 500M;
proxy_connect_timeout 600;
proxy_send_timeout 600;
proxy_read_timeout 600;
```

---

## 🔒 Security & Best Practices

### Storage Considerations

1. **Disk Space Monitoring**
   - Monitor `backend/uploaded_videos/` size regularly
   - Set up alerts for low disk space
   - Consider archiving old videos

2. **Backup Strategy**
   - Local storage acts as primary backup
   - Drive acts as cloud backup
   - Consider additional backups for critical videos

3. **Access Control**
   - Ensure `uploaded_videos/` directory is NOT publicly accessible via web
   - Videos should only be accessible via Drive links or authorized API calls

### Cleanup Script

Create a cleanup script for old videos (example):

```python
# cleanup_old_videos.py
import os
from datetime import datetime, timedelta

VIDEO_DIR = "backend/uploaded_videos"
DAYS_TO_KEEP = 30  # Keep videos for 30 days

cutoff_date = datetime.now() - timedelta(days=DAYS_TO_KEEP)

for filename in os.listdir(VIDEO_DIR):
    filepath = os.path.join(VIDEO_DIR, filename)
    if os.path.isfile(filepath):
        created = datetime.fromtimestamp(os.path.getctime(filepath))
        if created < cutoff_date:
            print(f"Deleting old video: {filename}")
            os.remove(filepath)
```

---

## 📈 Monitoring

### Key Metrics to Track

1. **Upload Success Rate**
   - Parse logs to count successful vs failed uploads
   - Alert if failure rate exceeds threshold

2. **Storage Usage**
   - Query `/api/videos/storage-stats` regularly
   - Set up alerts for storage thresholds

3. **Upload Duration**
   - Track time between upload start and completion
   - Identify performance bottlenecks

### Example Monitoring Query

```bash
# Count today's uploads
grep "Complete upload success" backend/logs/video_uploads.log | grep "$(date +%Y-%m-%d)" | wc -l

# Count failed Drive uploads
grep "Drive upload failed" backend/logs/video_uploads.log | grep "$(date +%Y-%m-%d)" | wc -l

# Total storage used
du -sh backend/uploaded_videos/
```

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] `backend/uploaded_videos/` directory exists
- [ ] `backend/logs/` directory exists
- [ ] Upload a test video via frontend
- [ ] Check video appears in `uploaded_videos/` folder
- [ ] Check video appears in Google Drive
- [ ] Verify log entry in `video_uploads.log`
- [ ] Test `/api/videos/list` endpoint
- [ ] Test `/api/videos/storage-stats` endpoint
- [ ] Simulate Drive failure (disable credentials) and verify local save still works
- [ ] Check `.gitignore` excludes video files

---

## 🎓 Training for Team

### For Content Uploaders

1. Upload videos as normal through the frontend
2. If upload fails, check the error message
3. If it says "Video saved locally", the video is safe - just retry or contact admin
4. Never upload the same video twice without checking with admin

### For Administrators

1. Regularly check storage stats: `GET /api/videos/storage-stats`
2. Monitor logs: `tail -f backend/logs/video_uploads.log`
3. Set up disk space alerts
4. Have a backup/archival strategy for old videos
5. Keep Drive credentials secure and up to date

---

## 🚀 Quick Start Commands

```bash
# Check storage usage
curl https://your-backend.com/api/videos/storage-stats

# List all videos
curl https://your-backend.com/api/videos/list

# View recent logs
tail -n 50 backend/logs/video_uploads.log

# Monitor uploads in real-time
tail -f backend/logs/video_uploads.log

# Check disk space
df -h backend/uploaded_videos/
```

---

## 📞 Support

If you encounter issues:

1. Check logs: `backend/logs/video_uploads.log`
2. Verify directories exist and have correct permissions
3. Test Drive connectivity
4. Check disk space
5. Review this documentation

**Remember: The system is designed so that NO VIDEO IS EVER LOST. If Drive fails, the video is still safe locally!**


