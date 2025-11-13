# Vercel Deployment Guide - Fix 403 Error

This guide will help you fix the 403 error you're experiencing with the `/api/add`, `/api/update`, and `/api/delete` endpoints on Vercel.

## Problem

The 403 error occurs because the backend requires Google Service Account credentials to write to your Google Sheet, but these credentials are not configured in your Vercel deployment.

## Solution Overview

1. Create Google Service Account credentials
2. Add credentials to Vercel as environment variables
3. Update code to read credentials from environment variables
4. Redeploy to Vercel

---

## Step 1: Create Google Service Account

### 1.1 Go to Google Cloud Console
Visit: https://console.cloud.google.com/

### 1.2 Create or Select a Project
- Click on the project dropdown at the top
- Click "New Project" or select an existing one
- Project name: `shortssprints` (or any name you prefer)

### 1.3 Enable Required APIs
1. Go to "APIs & Services" > "Library"
2. Search for "Google Sheets API" and click "Enable"
3. Search for "Google Drive API" and click "Enable"

### 1.4 Create Service Account
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Service account name: `sheets-api-service`
4. Click "Create and Continue"
5. Skip the optional steps, click "Done"

### 1.5 Create and Download Key
1. Find your service account in the list
2. Click on the service account email
3. Go to "Keys" tab
4. Click "Add Key" > "Create New Key"
5. Select "JSON" format
6. Click "Create" - a JSON file will be downloaded

### 1.6 Copy Service Account Email
From the downloaded JSON file, copy the `client_email` value. It looks like:
```
sheets-api-service@your-project.iam.gserviceaccount.com
```

---

## Step 2: Share Google Sheet with Service Account

1. Open your Google Sheet: https://docs.google.com/spreadsheets/d/1VV0v4_xmztdPlOS9iH-l6Aj6cTRDsifGdLj3QPQ0L0w
2. Click the "Share" button
3. Paste the service account email you copied
4. Set permission to "Editor"
5. **IMPORTANT**: Uncheck "Notify people"
6. Click "Share"

---

## Step 3: Add Credentials to Vercel

### Option A: Using Vercel Dashboard (Recommended)

1. Go to your Vercel project: https://vercel.com/dashboard
2. Select your `shortssprits-backend` project
3. Go to "Settings" > "Environment Variables"
4. Add the following variables:

#### Method 1: Add as Base64 (Recommended for Vercel)

First, convert your credentials.json to base64:

**On Mac/Linux:**
```bash
base64 -i /path/to/credentials.json | tr -d '\n' | pbcopy
```

**On Windows (PowerShell):**
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\path\to\credentials.json")) | Set-Clipboard
```

Then in Vercel:
- Variable name: `GOOGLE_CREDENTIALS_BASE64`
- Value: Paste the base64 string
- Environment: Production, Preview, Development
- Click "Add"

#### Also Add These Variables:

- Variable name: `SHEET_ID`
- Value: `1VV0v4_xmztdPlOS9iH-l6Aj6cTRDsifGdLj3QPQ0L0w`
- Click "Add"

- Variable name: `CREDENTIALS_GID`
- Value: `1409173850`
- Click "Add"

- Variable name: `JWT_SECRET_KEY`
- Value: Generate a secure key (see below)
- Click "Add"

**Generate JWT Secret:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Option B: Using Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Add environment variables
vercel env add GOOGLE_CREDENTIALS_BASE64
# Paste the base64 encoded credentials when prompted

vercel env add SHEET_ID
# Enter: 1VV0v4_xmztdPlOS9iH-l6Aj6cTRDsifGdLj3QPQ0L0w

vercel env add CREDENTIALS_GID
# Enter: 1409173850

vercel env add JWT_SECRET_KEY
# Enter your generated secret key
```

---

## Step 4: Update Backend Code to Use Environment Variables

The code needs to be updated to read credentials from environment variables instead of a file.

### Update `app.py`:

```python
def get_gspread_client():
    """Initialize gspread client with service account credentials"""
    try:
        # Check for base64 encoded credentials in environment (for Vercel)
        creds_base64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')

        if creds_base64:
            # Decode base64 credentials
            import base64
            creds_json = base64.b64decode(creds_base64).decode('utf-8')
            creds_dict = json.loads(creds_json)

            # Define the scope
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            # Authenticate using credentials dictionary
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            client = gspread.authorize(creds)
            return client

        # Fallback to local credentials.json file (for local development)
        creds_file = os.path.join(os.path.dirname(__file__), 'credentials.json')
        if os.path.exists(creds_file):
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
            client = gspread.authorize(creds)
            return client

        return None
    except Exception as e:
        print(f"Error initializing gspread client: {e}")
        import traceback
        traceback.print_exc()
        return None
```

I'll create a script to automatically update this for you.

---

## Step 5: Redeploy to Vercel

After adding the environment variables:

### Using Vercel Dashboard:
1. Go to your project's "Deployments" tab
2. Click on the latest deployment
3. Click the "..." menu
4. Click "Redeploy"
5. Check "Use existing Build Cache"
6. Click "Redeploy"

### Using Git:
```bash
# Commit your changes
git add .
git commit -m "Update credentials handling for Vercel"
git push origin main
```

Vercel will automatically redeploy.

### Using Vercel CLI:
```bash
vercel --prod
```

---

## Step 6: Verify the Fix

Once redeployed, test your endpoints:

### Test Add Entry:
```bash
curl -X POST https://shortssprits-backend.vercel.app/api/add \
  -H "Content-Type: application/json" \
  -d '{
    "Sr no.": "1",
    "Content Type": "Test",
    "Sub category": "Test Sub",
    "Exam name": "Test Exam",
    "Subject": "Test Subject",
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

### Test Update Entry:
```bash
curl -X PUT https://shortssprits-backend.vercel.app/api/update/0 \
  -H "Content-Type: application/json" \
  -d '{
    "Sr no.": "1",
    "Content Type": "Updated Test",
    "Sub category": "Updated Sub",
    "Exam name": "Updated Exam",
    "Subject": "Updated Subject",
    "Video Upload": "https://youtube.com/shorts/updated",
    "Edit": "Final",
    "Re-upload Link": ""
  }'
```

### Check Frontend:
1. Open your frontend: https://your-frontend.vercel.app
2. Try adding a new entry using the "Add New Entry" button
3. The 403 error should be gone!

---

## Troubleshooting

### Still Getting 403 Error?

1. **Check Environment Variables**:
   - Go to Vercel Dashboard > Settings > Environment Variables
   - Verify `GOOGLE_CREDENTIALS_BASE64` is set
   - Make sure it's enabled for Production

2. **Check Service Account Permissions**:
   - Verify you shared the Google Sheet with the service account email
   - Make sure permission is set to "Editor"

3. **Check Vercel Logs**:
   ```bash
   vercel logs
   ```
   Look for any error messages

4. **Redeploy**:
   Sometimes a fresh deployment is needed after adding environment variables

### Error: "Could not access Google Sheet"

- Double-check that you shared the sheet with the service account
- Verify the SHEET_ID is correct in environment variables
- Check that both Google Sheets API and Google Drive API are enabled

### Error: "Invalid credentials"

- Verify the base64 encoding is correct
- Make sure no extra whitespace in the environment variable
- Try re-downloading the service account key and encoding again

### Local Development

For local development, you can use `credentials.json` file:

1. Place `credentials.json` in the `backend/` folder
2. Make sure it's in `.gitignore` (already added)
3. The code will automatically use the file when `GOOGLE_CREDENTIALS_BASE64` is not set

---

## Security Notes

1. **Never commit `credentials.json`** to Git - it's already in `.gitignore`
2. **Keep your service account key secure** - treat it like a password
3. **Use environment variables** for production deployments
4. **Rotate keys periodically** - create new service account keys every few months
5. **Limit service account permissions** - only give it access to the specific sheet

---

## Summary

1. ✅ Create Google Service Account
2. ✅ Enable Google Sheets API and Google Drive API
3. ✅ Download service account JSON key
4. ✅ Share Google Sheet with service account email (as Editor)
5. ✅ Convert credentials to base64
6. ✅ Add `GOOGLE_CREDENTIALS_BASE64` to Vercel environment variables
7. ✅ Add other required environment variables (SHEET_ID, etc.)
8. ✅ Update code to read from environment variables
9. ✅ Redeploy to Vercel
10. ✅ Test the endpoints

After completing these steps, your 403 error should be resolved and you'll be able to add, update, and delete entries from your frontend!

---

## Quick Reference

### Environment Variables Required:
```
GOOGLE_CREDENTIALS_BASE64=<base64-encoded-credentials>
SHEET_ID=1VV0v4_xmztdPlOS9iH-l6Aj6cTRDsifGdLj3QPQ0L0w
CREDENTIALS_GID=1409173850
JWT_SECRET_KEY=<your-secret-key>
```

### Vercel Project URL:
- Backend: https://shortssprits-backend.vercel.app

### Google Sheet URL:
- https://docs.google.com/spreadsheets/d/1VV0v4_xmztdPlOS9iH-l6Aj6cTRDsifGdLj3QPQ0L0w

Need more help? Check the main setup guide: `GOOGLE_SHEETS_SETUP.md`
