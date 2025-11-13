# Authentication System - Quick Start Guide

This backend now includes a complete authentication system that uses your Google Sheet as the credential store.

## What's Been Added

### 1. New Dependencies
Updated `requirements.txt` with:
- `gspread` - Google Sheets API client
- `google-auth` - Google authentication
- `bcrypt` - Password hashing
- `PyJWT` - JWT token generation

### 2. New API Endpoints

#### Authentication Endpoints:
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/verify` - Verify JWT token
- `GET /api/auth/me` - Get current user info (requires auth)

### 3. Security Features
- **Password Hashing**: Passwords are hashed using bcrypt before storage
- **JWT Tokens**: Secure token-based authentication (7-day expiration)
- **Input Validation**: Email format, password strength, duplicate checks
- **Protected Routes**: Example decorator for protecting endpoints

## Quick Setup

### Option 1: With Google Service Account (Full Functionality)

Follow the detailed guide in `GOOGLE_SHEETS_SETUP.md` for complete setup with automatic signup.

**Quick Steps:**
1. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

2. Set up Google Service Account (see `GOOGLE_SHEETS_SETUP.md`)

3. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

4. Update `.env` with your values:
   ```env
   SHEET_ID=1VV0v4_xmztdPlOS9iH-l6Aj6cTRDsifGdLj3QPQ0L0w
   CREDENTIALS_GID=1409173850
   JWT_SECRET_KEY=your-secret-key-here
   ```

5. Start the server:
   ```bash
   python3 app.py
   ```

### Option 2: Manual Testing (No Service Account)

For quick testing without setting up service accounts:

1. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

2. Create `.env` file and add JWT secret

3. Manually add test user to your Google Sheet:
   - Open the sheet: https://docs.google.com/spreadsheets/d/1VV0v4_xmztdPlOS9iH-l6Aj6cTRDsifGdLj3QPQ0L0w/edit#gid=1409173850
   - Add a row with these values:
     - **Username**: `testuser`
     - **Email**: `test@example.com`
     - **New Password**: `$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYCxrqrXXqG`
     - **Confirm Password**: `$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYCxrqrXXqG`

4. Start the server:
   ```bash
   python3 app.py
   ```

5. Test login with:
   - Username: `testuser`
   - Password: `password123`

## Testing the Endpoints

### Using the Test Script
```bash
# Make sure server is running first
./test_auth.sh
```

### Manual cURL Tests

#### Signup (requires service account):
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "securepass123",
    "confirmPassword": "securepass123"
  }'
```

#### Login:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

#### Verify Token:
```bash
# Replace YOUR_TOKEN with the token from login response
curl -X GET http://localhost:5000/api/auth/verify \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Get Current User:
```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## How It Works

### Data Flow

1. **Signup**:
   - User submits username, email, password
   - Backend validates input
   - Password is hashed with bcrypt
   - Credentials are written to Google Sheet
   - JWT token is generated and returned

2. **Login**:
   - User submits username and password
   - Backend fetches users from Google Sheet
   - Password is verified against stored hash
   - JWT token is generated and returned

3. **Protected Routes**:
   - Client sends JWT token in Authorization header
   - Backend verifies token
   - If valid, request proceeds
   - If invalid/expired, returns 401 error

### Google Sheet Structure

The credentials are stored in the sheet with this structure:
```
| Username | Email           | New Password (hash)      | Confirm Password (hash) |
|----------|-----------------|--------------------------|-------------------------|
| testuser | test@example.com| $2b$12$LQv3c1yqB...   | $2b$12$LQv3c1yqB...   |
```

## Code Examples

### Protecting a Route
```python
@app.route('/api/protected-endpoint', methods=['GET'])
@token_required
def protected_route(current_user):
    # current_user contains the authenticated username
    return jsonify({
        'message': f'Hello {current_user}!',
        'data': 'This is protected data'
    })
```

### Frontend Integration (JavaScript)
```javascript
// Signup
const signup = async (username, email, password, confirmPassword) => {
  const response = await fetch('http://localhost:5000/api/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password, confirmPassword })
  });
  const data = await response.json();
  if (data.success) {
    localStorage.setItem('token', data.token);
    localStorage.setItem('user', JSON.stringify(data.user));
  }
  return data;
};

// Login
const login = async (username, password) => {
  const response = await fetch('http://localhost:5000/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  if (data.success) {
    localStorage.setItem('token', data.token);
    localStorage.setItem('user', JSON.stringify(data.user));
  }
  return data;
};

// Make authenticated requests
const fetchProtectedData = async () => {
  const token = localStorage.getItem('token');
  const response = await fetch('http://localhost:5000/api/auth/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
};

// Logout
const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};
```

## Environment Variables

Required in `.env`:
```env
# Google Sheets
SHEET_ID=your-sheet-id
CREDENTIALS_GID=your-credentials-tab-gid

# JWT
JWT_SECRET_KEY=your-very-secure-secret-key

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
```

## Security Best Practices

1. **Never commit `credentials.json`** - Already in `.gitignore`
2. **Use strong JWT secret** - Generate with: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
3. **Use HTTPS in production** - Tokens are vulnerable over HTTP
4. **Implement rate limiting** - Prevent brute force attacks
5. **Add password complexity rules** - Current minimum is 6 characters
6. **Consider adding email verification** - Verify email addresses are real
7. **Add refresh tokens** - For better security with shorter-lived access tokens

## Troubleshooting

### Server won't start
```bash
# Check Python version
python3 --version  # Should be 3.7+

# Install dependencies
pip3 install -r requirements.txt

# Check for errors
python3 app.py
```

### Signup returns 503
- Service account credentials not set up
- Follow `GOOGLE_SHEETS_SETUP.md`
- OR manually add users to sheet for testing

### Login returns 401
- Check username and password
- Verify user exists in Google Sheet
- Check password hash is correct

### Token errors
- Verify JWT_SECRET_KEY is set in `.env`
- Check token format: `Bearer <token>`
- Token may have expired (7 day limit)

## Next Steps

1. **Set up Google Service Account** - Enable automatic signup
2. **Add to frontend** - Create login/signup UI
3. **Add password reset** - Email-based password recovery
4. **Add user roles** - Admin, user, etc.
5. **Add rate limiting** - Prevent abuse
6. **Add email verification** - Verify email addresses
7. **Add 2FA** - Two-factor authentication

## Files Modified/Created

- ✓ `app.py` - Added authentication endpoints and logic
- ✓ `requirements.txt` - Added new dependencies
- ✓ `.env.example` - Added JWT secret and credentials GID
- ✓ `GOOGLE_SHEETS_SETUP.md` - Complete setup guide
- ✓ `AUTH_README.md` - This file
- ✓ `test_auth.sh` - Test script
- ✓ `.gitignore` - Already includes credentials.json

## Support

For detailed setup instructions, see `GOOGLE_SHEETS_SETUP.md`

For API documentation, see the "Available Endpoints" section in `GOOGLE_SHEETS_SETUP.md`
