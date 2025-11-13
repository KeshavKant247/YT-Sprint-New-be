# Fix 403 Error - Quick Guide

## The Problem

You're getting this error:
```
shortssprits-backend.vercel.app/api/add: Failed to load resource: the server responded with a status of 403 ()
```

This happens because:
- The backend needs Google Service Account credentials to write to Google Sheets
- These credentials are not configured in your Vercel deployment
- Without credentials, the API returns 403 (Forbidden)

## The Solution (3 Main Steps)

### Step 1: Create Google Service Account & Get Credentials

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create/Select Project**: Create a new project or use existing
3. **Enable APIs**:
   - Enable "Google Sheets API"
   - Enable "Google Drive API"
4. **Create Service Account**:
   - Go to APIs & Services > Credentials
   - Create Credentials > Service Account
   - Name it something like "sheets-api"
   - Download the JSON key file
5. **Save the email**: Copy the service account email (looks like `name@project.iam.gserviceaccount.com`)

### Step 2: Share Your Google Sheet

1. Open your sheet: https://docs.google.com/spreadsheets/d/1VV0v4_xmztdPlOS9iH-l6Aj6cTRDsifGdLj3QPQ0L0w
2. Click "Share"
3. Paste the service account email
4. Give it "Editor" permission
5. **Uncheck "Notify people"**
6. Click "Share"

### Step 3: Add Credentials to Vercel

#### 3A. Encode Your Credentials

**Option 1: Use the script (easiest)**
```bash
cd backend
./encode_credentials.sh
```
The script will encode and copy the credentials to your clipboard.

**Option 2: Manual encoding**

On Mac/Linux:
```bash
base64 -i credentials.json | tr -d '\n' | pbcopy
```

On Windows PowerShell:
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("credentials.json")) | Set-Clipboard
```

#### 3B. Add to Vercel

1. Go to https://vercel.com/dashboard
2. Select your `shortssprits-backend` project
3. Go to **Settings** > **Environment Variables**
4. Add these variables:

| Variable Name | Value |
|--------------|-------|
| `GOOGLE_CREDENTIALS_BASE64` | Paste the base64 encoded credentials |
| `SHEET_ID` | `1VV0v4_xmztdPlOS9iH-l6Aj6cTRDsifGdLj3QPQ0L0w` |
| `CREDENTIALS_GID` | `1409173850` |
| `JWT_SECRET_KEY` | Generate: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` |

5. Make sure to select **All** environments (Production, Preview, Development)
6. Click **Save**

#### 3C. Redeploy

1. Go to **Deployments** tab
2. Click on the latest deployment
3. Click **"..."** menu > **Redeploy**
4. Click **Redeploy**

## Test It

After redeployment (takes ~2 minutes), test:

```bash
curl -X POST https://shortssprits-backend.vercel.app/api/add \
  -H "Content-Type: application/json" \
  -d '{
    "Sr no.": "999",
    "Content Type": "Test",
    "Sub category": "Testing",
    "Exam name": "Test Exam",
    "Subject": "Test",
    "Video Upload": "https://youtube.com/shorts/test",
    "Edit": "Final",
    "Re-upload Link": ""
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "Row added successfully"
}
```

## Visual Checklist

- [ ] Created Google Service Account
- [ ] Enabled Google Sheets API
- [ ] Enabled Google Drive API
- [ ] Downloaded JSON credentials
- [ ] Shared Google Sheet with service account email (as Editor)
- [ ] Encoded credentials to base64
- [ ] Added `GOOGLE_CREDENTIALS_BASE64` to Vercel
- [ ] Added `SHEET_ID` to Vercel
- [ ] Added `CREDENTIALS_GID` to Vercel
- [ ] Added `JWT_SECRET_KEY` to Vercel
- [ ] Redeployed on Vercel
- [ ] Tested the API endpoint

## Still Not Working?

### Check Vercel Logs
```bash
vercel logs --prod
```

### Common Issues

1. **"Could not access Google Sheet"**
   - Make sure you shared the sheet with the service account
   - Verify the service account has "Editor" permission

2. **"Invalid credentials"**
   - Check that base64 encoding doesn't have line breaks
   - Try encoding again

3. **Still 403 after adding credentials**
   - Wait a few minutes for Vercel to propagate the changes
   - Try a hard redeploy (without cache)
   - Check that environment variables are set for all environments

4. **Works locally but not on Vercel**
   - Verify `GOOGLE_CREDENTIALS_BASE64` is set in Vercel
   - Check Vercel logs for specific error messages

## What Changed in the Code

The backend has been updated to:
1. ✅ Implement actual add/update/delete functionality using gspread
2. ✅ Support both local `credentials.json` file and environment variable
3. ✅ Work seamlessly on both local development and Vercel production

Files modified:
- `app.py` - Updated credential loading and implemented write operations
- `.env.example` - Added `GOOGLE_CREDENTIALS_BASE64` variable

Files created:
- `VERCEL_DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `encode_credentials.sh` - Helper script to encode credentials
- `FIX_403_ERROR.md` - This quick reference

## Need More Help?

For detailed step-by-step instructions with screenshots:
- See `VERCEL_DEPLOYMENT_GUIDE.md`

For Google Service Account setup:
- See `GOOGLE_SHEETS_SETUP.md`

For authentication setup:
- See `AUTH_README.md`
