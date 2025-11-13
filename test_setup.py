#!/usr/bin/env python3
"""Quick test to verify Google Sheets/Drive setup"""

import json
import os
from google.oauth2.service_account import Credentials
import gspread

# Load credentials
with open('credentials.json', 'r') as f:
    creds = json.load(f)

print("=" * 60)
print("GOOGLE SHEETS/DRIVE SETUP VERIFICATION")
print("=" * 60)
print()

# Show service account email
service_email = creds.get('client_email')
print(f"✓ Service Account Email: {service_email}")
print()

# Test gspread connection
print("Testing Google Sheets connection...")
try:
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    credentials = Credentials.from_service_account_file('credentials.json', scopes=scopes)
    client = gspread.authorize(credentials)
    print("✓ Google Sheets client initialized successfully")

    # Try to open the sheet
    SHEET_ID = '1VV0v4_xmztdPlOS9iH-l6Aj6cTRDsifGdLj3QPQ0L0w'
    print(f"\nTrying to access sheet: {SHEET_ID}")

    spreadsheet = client.open_by_key(SHEET_ID)
    print(f"✓ Successfully opened spreadsheet: {spreadsheet.title}")

    # Get first worksheet
    worksheet = spreadsheet.get_worksheet(0)
    print(f"✓ Successfully accessed worksheet: {worksheet.title}")

    # Get headers
    headers = worksheet.row_values(1)
    print(f"✓ Sheet headers: {headers}")

    print()
    print("=" * 60)
    print("✅ SETUP IS CORRECT - Backend should work!")
    print("=" * 60)
    print()
    print("If you're still getting 403 errors:")
    print("1. Make sure the backend server is running")
    print("2. Restart the backend server: python3 app.py")
    print("3. Check that the frontend is pointing to the correct backend URL")

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("=" * 60)
    print("🔧 HOW TO FIX")
    print("=" * 60)
    print()
    print("The Google Sheet is NOT shared with your service account!")
    print()
    print("Follow these steps:")
    print()
    print(f"1. Copy this email: {service_email}")
    print()
    print("2. Open your Google Sheet:")
    print("   https://docs.google.com/spreadsheets/d/1VV0v4_xmztdPlOS9iH-l6Aj6cTRDsifGdLj3QPQ0L0w")
    print()
    print("3. Click the 'Share' button (top right)")
    print()
    print(f"4. Paste the email: {service_email}")
    print()
    print("5. Set permission to 'Editor'")
    print()
    print("6. UNCHECK 'Notify people'")
    print()
    print("7. Click 'Share'")
    print()
    print("8. Also share your Google Drive folder:")
    print("   https://drive.google.com/drive/folders/1m5gFfXB0AifbAn387sTM_mr8gemi1Jte")
    print()
    print("9. Run this script again to verify")
    print()
