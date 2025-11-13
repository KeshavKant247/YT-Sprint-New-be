# Video Upload to Google Drive - Setup Guide

## 🔴 CRITICAL SECURITY WARNING

**IMPORTANT**: You have shared your service account private key publicly in the chat. This is a **MAJOR SECURITY RISK**.

### Immediate Actions Required:

1. **Delete the Compromised Service Account**:
   - Go to https://console.cloud.google.com/iam-admin/serviceaccounts
   - Find: `drive-access-service@rare-shadow-467804-c6.iam.gserviceaccount.com`
   - Delete this service account

2. **Create a New Service Account**:
   - Follow the steps below to create a fresh service account
   - Download the new JSON key
   - **NEVER share it publicly again**

3. **Security Best Practices**:
   - Treat service account keys like passwords
   - Never commit them to Git
   - Never share them in chat/email
   - Store them securely (use environment variables in production)
   - Rotate keys periodically

---

## What's Been Implemented

### Backend Features:
1. **Google Drive API Integration** - Upload videos to your specific Drive folder
2. **Video Upload Endpoint** - `/api/upload-video` endpoint for file uploads
3. **Automatic VideoId Storage** - Stores the Drive file ID in the sheet
4. **Public Link Generation** - Makes uploaded videos accessible via link

### Frontend Features:
1. **Updated Form Structure** - Matches your Google Sheet columns:
   - Sr no.
   - Exam Name
   - Subject
   - Type of Content
   - Sub category
   - Video Link
   - Edit
   - Editor Brief
   - Final Edited Link
   - VideoId

2. **Video File Upload** - Upload video files when "Edit" status is "Re-edit"
3. **Automatic Drive Upload** - Videos are uploaded to Drive on form submit
4. **VideoId Auto-population** - Drive file ID is automatically added to the sheet

---

## Setup Instructions

### Step 1: Create New Service Account (After Deleting Old One)

1. **Go to Google Cloud Console**:
   https://console.cloud.google.com/

2. **Select Your Project**:
   - Project ID: `rare-shadow-467804-c6`
   - Or create a new project for better security

3. **Enable Required APIs**:
   - Go to "APIs & Services" > "Library"
   - Enable "Google Drive API"
   - Enable "Google Sheets API"

4. **Create Service Account**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Name: `video-uploader-service` (or any name)
   - Click "Create and Continue"
   - Skip optional steps, click "Done"

5. **Download JSON Key**:
   - Click on the service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Select "JSON"
   - Click "Create"
   - Save as `credentials.json` in the `backend/` folder

### Step 2: Share Google Drive Folder

1. **Get Service Account Email**:
   From credentials.json, copy the `client_email` value

2. **Share Drive Folder**:
   - Open: https://drive.google.com/drive/folders/1m5gFfXB0AifbAn387sTM_mr8gemi1Jte
   - Click "Share"
   - Paste the service account email
   - Set permission to "Editor"
   - **Uncheck "Notify people"**
   - Click "Share"

3. **Share Google Sheet**:
   - Open: https://docs.google.com/spreadsheets/d/1VV0v4_xmztdPlOS9iH-l6Aj6cTRDsifGdLj3QPQ0L0w
   - Click "Share"
   - Paste the service account email
   - Set permission to "Editor"
   - **Uncheck "Notify people"**
   - Click "Share"

### Step 3: Install Dependencies

```bash
cd backend
pip3 install -r requirements.txt
```

New dependencies added:
- `google-api-python-client==2.108.0` - For Google Drive API

### Step 4: Configure Environment Variables

Create `.env` file in backend folder:

```env
# Google Sheets Configuration
SHEET_ID=1VV0v4_xmztdPlOS9iH-l6Aj6cTRDsifGdLj3QPQ0L0w
CREDENTIALS_GID=1409173850

# Google Drive Configuration
DRIVE_FOLDER_ID=1m5gFfXB0AifbAn387sTM_mr8gemi1Jte

# JWT Configuration (generate a new one!)
JWT_SECRET_KEY=your-new-secret-key-here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

Generate new JWT secret:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 5: Test Locally

1. **Start Backend**:
   ```bash
   cd backend
   python3 app.py
   ```

2. **Start Frontend** (in another terminal):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test Video Upload**:
   - Open frontend in browser
   - Click "Add New Entry"
   - Fill in required fields
   - Select "Re-edit" for Edit Status
   - Upload a video file
   - Submit form
   - Check Google Drive folder for uploaded video
   - Check Google Sheet for VideoId

---

## How It Works

### Upload Flow:

1. **User fills form** and selects a video file
2. **Frontend uploads** video to `/api/upload-video` endpoint
3. **Backend uploads** video to Google Drive folder
4. **Drive returns** video ID (file ID)
5. **Backend makes** video publicly accessible (anyone with link)
6. **Frontend receives** video ID and Drive link
7. **Frontend submits** form data with VideoId to `/api/add`
8. **Backend stores** all data including VideoId in Google Sheet

### File Structure in Drive:

```
Video Uploads Folder (1m5gFfXB0AifbAn387sTM_mr8gemi1Jte)
├── video1.mp4 (ID: abc123...)
├── video2.mp4 (ID: def456...)
└── video3.mp4 (ID: ghi789...)
```

### Sheet Structure:

| Sr no. | Exam Name | Subject | Type of Content | Sub category | Video Link | Edit | Editor Brief | Final Edited Link | VideoId |
|--------|-----------|---------|----------------|--------------|------------|------|--------------|------------------|---------|
| 1      | IBPS PO   | Maths   | Content        | Tips         | youtube... | Re-edit | Fix audio | drive.google.com/file/d/abc123 | abc123 |

---

## API Endpoints

### Upload Video
```
POST /api/upload-video
Content-Type: multipart/form-data

Body: FormData with 'video' file
```

**Response:**
```json
{
  "success": true,
  "video_id": "1A2B3C4D5E6F...",
  "drive_link": "https://drive.google.com/file/d/1A2B3C4D5E6F.../view",
  "filename": "my-video.mp4"
}
```

### Add Entry (with VideoId)
```
POST /api/add
Content-Type: application/json

Body:
{
  "Sr no.": "1",
  "Exam Name": "IBPS PO",
  "Subject": "Maths",
  "Type of Content": "Content",
  "Sub category": "Tips & Tricks",
  "Video Link": "https://youtube.com/shorts/...",
  "Edit": "Re-edit",
  "Editor Brief": "Fix audio quality",
  "Final Edited Link": "https://drive.google.com/file/d/...",
  "VideoId": "1A2B3C4D5E6F..."
}
```

---

## Deployment to Vercel

### Update Environment Variables:

1. **Encode Credentials** (after creating new service account):
   ```bash
   cd backend
   ./encode_credentials.sh
   ```

2. **Add to Vercel**:
   - Variable: `GOOGLE_CREDENTIALS_BASE64`
   - Value: (paste the base64 encoded credentials)

3. **Also Add**:
   - `DRIVE_FOLDER_ID=1m5gFfXB0AifbAn387sTM_mr8gemi1Jte`
   - `SHEET_ID=1VV0v4_xmztdPlOS9iH-l6Aj6cTRDsifGdLj3QPQ0L0w`
   - `CREDENTIALS_GID=1409173850`
   - `JWT_SECRET_KEY=your-new-secret-key`

4. **Redeploy**

---

## Troubleshooting

### "Could not initialize Drive service"
- Verify credentials.json exists in backend folder
- Check service account has Drive API enabled
- Verify GOOGLE_CREDENTIALS_BASE64 is set (for Vercel)

### "Failed to upload video"
- Check Drive folder is shared with service account
- Verify service account has "Editor" permission
- Check file size (Drive has limits)

### "Permission denied"
- Service account doesn't have access to folder
- Re-share the folder with service account email

### VideoId not appearing in sheet
- Check sheet is shared with service account
- Verify column "VideoId" exists in sheet
- Check API logs for errors

---

## Security Checklist

- [ ] Deleted the compromised service account
- [ ] Created new service account
- [ ] credentials.json is in `.gitignore`
- [ ] Never shared private key publicly
- [ ] Using environment variables for production
- [ ] JWT_SECRET_KEY is strong and secret
- [ ] Drive folder permissions are correct
- [ ] Sheet permissions are correct

---

## File Size Limits

- **Google Drive**: 5TB per file (individual files)
- **Recommended**: Keep videos under 1GB for best performance
- **Format**: MP4, MOV, AVI supported

---

## Cost Considerations

- **Google Drive Storage**: 15GB free, then paid plans
- **API Calls**: Free tier usually sufficient
- **Monitor Usage**: Check Google Cloud Console for usage

---

## Need Help?

1. Check Vercel logs: `vercel logs --prod`
2. Check backend logs: Look at Flask console output
3. Test locally first before deploying
4. Verify all environment variables are set

---

## Summary

✅ Video upload to Google Drive implemented
✅ VideoId automatically stored in Google Sheet
✅ Public sharing enabled for uploaded videos
✅ Form updated to match sheet structure
✅ Backend and frontend integrated

🔴 **REMEMBER**: Delete the old compromised service account and create a new one!
