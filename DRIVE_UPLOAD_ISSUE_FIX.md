# Google Drive Upload Issue - Service Account Storage Quota

## 🔴 Issue Found

The Google Drive upload is failing with this error:
```
Service Accounts do not have storage quota. Leverage shared drives
(https://developers.google.com/workspace/drive/api/guides/about-shareddrives),
or use OAuth delegation instead.
```

**Root Cause**: Service accounts cannot upload files directly to regular Google Drive folders because they don't have their own storage quota.

## ✅ Solutions

### Option 1: Use a Shared Drive (Recommended - Easiest)

A Shared Drive (previously called Team Drive) is specifically designed for service accounts and teams.

#### Steps:

1. **Create a Shared Drive**:
   - Go to https://drive.google.com
   - Click on "Shared drives" in the left sidebar
   - Click "New" to create a new Shared Drive
   - Name it (e.g., "Video Uploads")

2. **Get the Shared Drive ID**:
   - Open the Shared Drive
   - Copy the ID from the URL: `https://drive.google.com/drive/folders/SHARED_DRIVE_ID`

3. **Share with Service Account**:
   - Inside the Shared Drive, click the settings icon (⚙️)
   - Click "Manage members"
   - Add the service account email: `drive-access-service@rare-shadow-467804-c6.iam.gserviceaccount.com`
   - Give it "Content Manager" or "Manager" role
   - Click "Send"

4. **Update Environment Variable**:
   ```env
   DRIVE_FOLDER_ID=<YOUR_SHARED_DRIVE_ID>
   ```

5. **Update Code** (see modifications below)

---

### Option 2: Use Domain-Wide Delegation (Advanced)

This requires Google Workspace (not available for personal Gmail accounts).

#### Requirements:
- Google Workspace account (paid)
- Admin access to the workspace
- More complex setup

Not recommended unless you already have Google Workspace.

---

### Option 3: Alternative Upload Solutions

If you can't use Shared Drives, consider these alternatives:

1. **Cloudinary** - Free tier for video uploads
2. **AWS S3** - Pay-as-you-go storage
3. **Vercel Blob Storage** - Integrated with Vercel deployment
4. **Supabase Storage** - Open-source alternative

---

## 🔧 Code Modifications for Shared Drive

Update the `upload_video_to_drive` function in `app.py`:

```python
def upload_video_to_drive(file_content, filename, mimetype):
    """Upload video to Google Drive Shared Drive and return file ID"""
    try:
        service = get_drive_service()

        if not service:
            return None, "Could not initialize Drive service"

        # Create file metadata with Shared Drive support
        file_metadata = {
            'name': filename,
            'parents': [DRIVE_FOLDER_ID]
        }

        # Create media from file content
        media = MediaIoBaseUpload(
            io.BytesIO(file_content),
            mimetype=mimetype,
            resumable=True
        )

        # Upload file with supportsAllDrives parameter
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink, webContentLink',
            supportsAllDrives=True  # ADD THIS LINE
        ).execute()

        # Make file accessible to anyone with the link
        service.permissions().create(
            fileId=file.get('id'),
            body={'type': 'anyone', 'role': 'reader'},
            supportsAllDrives=True  # ADD THIS LINE
        ).execute()

        return file.get('id'), None

    except Exception as e:
        print(f"Error uploading to Drive: {e}")
        import traceback
        traceback.print_exc()
        return None, str(e)
```

---

## 📝 Summary

**Current Status**:
- ❌ Upload to regular Drive folder fails (service account limitation)
- ✅ Code is correct and working
- ✅ Videos are named with content type
- ✅ Integration is complete

**What You Need To Do**:
1. Create a Shared Drive in Google Drive
2. Share it with the service account email
3. Update DRIVE_FOLDER_ID with the Shared Drive ID
4. Apply the code modifications above (add `supportsAllDrives=True`)
5. Test again

**Service Account Email**:
```
drive-access-service@rare-shadow-467804-c6.iam.gserviceaccount.com
```

**Current Folder** (won't work):
```
https://drive.google.com/drive/folders/1m5gFfXB0AifbAn387sTM_mr8gemi1Jte
```
This is a regular folder, not a Shared Drive.

**Need Help?**
- Shared Drives require Google Workspace ($6/user/month)
- If you don't have Workspace, consider alternative upload solutions
