# Google Sheets API Setup Guide

This guide will help you set up Google Service Account credentials to enable write operations (signup functionality) to your Google Sheet.

## Prerequisites
- A Google Cloud Platform account
- The Google Sheet you want to write to

## Step-by-Step Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "Adda Education Auth")
5. Click "Create"

### 2. Enable Required APIs

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Sheets API" and click on it
3. Click "Enable"
4. Go back to the Library and search for "Google Drive API"
5. Click on it and then click "Enable"

### 3. Create a Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Enter a service account name (e.g., "sheets-auth-service")
4. Click "Create and Continue"
5. Skip the optional steps by clicking "Continue" and then "Done"

### 4. Create and Download Service Account Key

1. On the Credentials page, find your newly created service account
2. Click on the service account email
3. Go to the "Keys" tab
4. Click "Add Key" > "Create New Key"
5. Select "JSON" as the key type
6. Click "Create"
7. A JSON file will be downloaded to your computer

### 5. Configure the Backend

1. Rename the downloaded JSON file to `credentials.json`
2. Move it to your backend folder:
   ```bash
   mv ~/Downloads/your-project-name-*.json /path/to/backend/credentials.json
   ```
3. **Important**: Add `credentials.json` to your `.gitignore` file to avoid committing sensitive credentials

### 6. Share Google Sheet with Service Account

1. Open your Google Sheet
2. Find the service account email in the `credentials.json` file (it looks like: `service-account-name@project-id.iam.gserviceaccount.com`)
3. Click "Share" button in your Google Sheet
4. Paste the service account email
5. Grant "Editor" access
6. Click "Send"

### 7. Set Environment Variables

Make sure your `.env` file has the following variables:

```env
SHEET_ID=1VV0v4_xmztdPlOS9iH-l6Aj6cTRDsifGdLj3QPQ0L0w
CREDENTIALS_GID=1409173850
JWT_SECRET_KEY=your-very-secure-random-secret-key-here
```

**Generate a secure JWT secret key**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 8. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 9. Test the Setup

Start the Flask server:
```bash
python app.py
```

Test signup endpoint:
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "confirmPassword": "password123"
  }'
```

If successful, you should see a response with a JWT token and the user should be added to your Google Sheet!

## Available Endpoints

### Authentication Endpoints

#### 1. Signup
```
POST /api/auth/signup
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123",
  "confirmPassword": "securepass123"
}
```

**Success Response (201)**:
```json
{
  "success": true,
  "message": "User registered successfully",
  "token": "eyJhbGc...",
  "user": {
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

#### 2. Login
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepass123"
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGc...",
  "user": {
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

#### 3. Verify Token
```
GET /api/auth/verify
Authorization: Bearer <your-token>
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Token is valid",
  "username": "johndoe"
}
```

#### 4. Get Current User
```
GET /api/auth/me
Authorization: Bearer <your-token>
```

**Success Response (200)**:
```json
{
  "success": true,
  "user": {
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

## Security Notes

1. **Never commit `credentials.json`** - Add it to `.gitignore`
2. **Keep JWT_SECRET_KEY secure** - Use a strong random key
3. **Passwords are hashed** - The system uses bcrypt to hash passwords before storing
4. **HTTPS in production** - Always use HTTPS in production to protect tokens
5. **Token expiration** - Tokens expire after 7 days
6. **Password requirements** - Minimum 6 characters (adjust in code as needed)

## Troubleshooting

### "Google Service Account credentials not found"
- Make sure `credentials.json` is in the backend folder
- Check file permissions

### "Worksheet with gid not found"
- Verify the CREDENTIALS_GID in your `.env` file
- Make sure the sheet tab exists

### "Permission denied" when writing to sheet
- Ensure you shared the sheet with the service account email
- Grant "Editor" access to the service account

### Token errors
- Check that JWT_SECRET_KEY is set in `.env`
- Verify the token is being sent in the Authorization header as "Bearer <token>"

## Manual Testing Alternative

If you want to test login without setting up service accounts:

1. Manually add a test user to your Google Sheet:
   - Username: `testuser`
   - Email: `test@example.com`
   - New Password: Use this bcrypt hash: `$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYCxrqrXXqG`
   - Confirm Password: Same hash as above

2. The password for this hash is: `password123`

3. Test login:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

## Production Deployment

For production deployment on Vercel or other platforms:

1. Add `credentials.json` content as an environment variable
2. Modify the code to read credentials from the environment variable instead of a file
3. Use strong JWT secrets
4. Enable HTTPS
5. Consider rate limiting for auth endpoints
6. Add proper logging and monitoring
