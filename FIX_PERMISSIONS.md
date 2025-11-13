# Fix Permission Error (403 PERMISSION_DENIED)

## The Problem

You're seeing this error:
```
The caller does not have permission - PERMISSION_DENIED
```

This means the Google Sheet can be READ but not WRITTEN to. The service account needs Editor permission.

## The Solution

### Step 1: Copy Service Account Email

```
drive-access-service@rare-shadow-467804-c6.iam.gserviceaccount.com
```

**Copy this email!** ☝️

### Step 2: Share the Google Sheet

1. **Open your Google Sheet**:
   https://docs.google.com/spreadsheets/d/1VV0v4_xmztdPlOS9iH-l6Aj6cTRDsifGdLj3QPQ0L0w

2. **Click "Share" button** (top right corner)

3. **Paste the email**:
   ```
   drive-access-service@rare-shadow-467804-c6.iam.gserviceaccount.com
   ```

4. **Change permission from "Viewer" to "Editor"**
   - Click the dropdown next to the email
   - Select **"Editor"** (NOT Viewer or Commenter)

5. **UNCHECK "Notify people"**
   - Important: The service account is not a real person

6. **Click "Share"** or "Done"

### Step 3: Also Share the Drive Folder

1. **Open the Drive folder**:
   https://drive.google.com/drive/folders/1m5gFfXB0AifbAn387sTM_mr8gemi1Jte

2. **Click "Share"**

3. **Paste the same email**:
   ```
   drive-access-service@rare-shadow-467804-c6.iam.gserviceaccount.com
   ```

4. **Set permission to "Editor"**

5. **UNCHECK "Notify people"**

6. **Click "Share"**

### Step 4: Test Again

After sharing, try adding an entry again from the frontend.

Or test with curl:
```bash
curl -X POST http://localhost:5000/api/add \
  -H "Content-Type: application/json" \
  -d '{
    "Sr no.": "1",
    "Exam Name": "Test",
    "Subject": "Math",
    "Type of Content": "Content",
    "Sub category": "Tips & Tricks / Shortcuts",
    "Video Link": "https://youtube.com/test",
    "Edit": "Final",
    "Editor Brief": "",
    "Final Edited Link": "",
    "VideoId": ""
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "Row added successfully"
}
```

## Visual Guide

When sharing the sheet, it should look like this:

```
┌─────────────────────────────────────────────┐
│  Share "Umesh hackathon dashboard"         │
├─────────────────────────────────────────────┤
│                                             │
│  Add people, groups, and calendar events   │
│  ┌──────────────────────────────────────┐  │
│  │ drive-access-service@rare-shadow...  │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  Permission: [Editor ▼]  ← Select "Editor" │
│                                             │
│  □ Notify people  ← UNCHECK this           │
│                                             │
│  [Cancel]  [Share]                          │
└─────────────────────────────────────────────┘
```

## Check Current Permissions

To see who has access to your sheet:
1. Open the sheet
2. Click "Share"
3. Look for: `drive-access-service@rare-shadow-467804-c6.iam.gserviceaccount.com`
4. Make sure it says **"Editor"** next to it

## Common Mistakes

❌ **Viewer access** - Can read but not write
❌ **Commenter access** - Can read but not edit
✅ **Editor access** - Can read AND write (This is what you need!)

## Still Not Working?

If you still get permission errors after sharing:

1. **Double-check the email is EXACTLY**:
   ```
   drive-access-service@rare-shadow-467804-c6.iam.gserviceaccount.com
   ```

2. **Make sure permission is "Editor"**

3. **Wait 1-2 minutes** for Google to propagate the permissions

4. **Refresh the frontend page** and try again

## Success!

When it works, you'll see:
- ✅ Entry added to Google Sheet
- ✅ New row appears in the table
- ✅ No error messages

---

**Note**: After you fix this, you should delete this compromised service account and create a new one (see VIDEO_UPLOAD_SETUP.md for security warning).
