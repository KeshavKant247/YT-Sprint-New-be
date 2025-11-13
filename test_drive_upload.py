#!/usr/bin/env python3
"""
Test script to verify Google Drive upload functionality
"""
import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

load_dotenv()

DRIVE_FOLDER_ID = os.getenv('DRIVE_FOLDER_ID', '1m5gFfXB0AifbAn387sTM_mr8gemi1Jte')

def get_drive_service():
    """Initialize Google Drive service"""
    try:
        # Define the scope
        scopes = [
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive'
        ]

        # Try loading credentials.json
        creds_file = os.path.join(os.path.dirname(__file__), 'credentials.json')
        if os.path.exists(creds_file):
            creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
            service = build('drive', 'v3', credentials=creds)
            return service

        return None
    except Exception as e:
        print(f"Error initializing Drive service: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_drive_upload():
    """Test uploading a small test file to Drive"""
    try:
        print("=" * 60)
        print("Testing Google Drive Upload")
        print("=" * 60)

        # Initialize Drive service
        print("\n1. Initializing Drive service...")
        service = get_drive_service()

        if not service:
            print("❌ Failed to initialize Drive service")
            return False

        print("✅ Drive service initialized successfully")

        # Check if folder exists and is accessible
        print(f"\n2. Checking access to folder: {DRIVE_FOLDER_ID}")
        try:
            folder = service.files().get(fileId=DRIVE_FOLDER_ID, fields='id, name').execute()
            print(f"✅ Folder accessible: {folder.get('name')}")
        except Exception as e:
            print(f"❌ Cannot access folder: {e}")
            print("\nPlease ensure:")
            print(f"   - Folder ID is correct: {DRIVE_FOLDER_ID}")
            print(f"   - Service account has access to the folder")
            print(f"   - Service account email: Check credentials.json for 'client_email'")
            return False

        # Create a small test file
        print("\n3. Creating test file...")
        test_content = b"This is a test video file for Drive upload verification"
        test_filename = "TEST_Content_test_upload.txt"

        # Create file metadata
        file_metadata = {
            'name': test_filename,
            'parents': [DRIVE_FOLDER_ID]
        }

        # Upload test file
        print(f"4. Uploading test file: {test_filename}")
        media = MediaIoBaseUpload(
            io.BytesIO(test_content),
            mimetype='text/plain',
            resumable=True
        )

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink, webContentLink'
        ).execute()

        file_id = file.get('id')
        print(f"✅ File uploaded successfully!")
        print(f"   File ID: {file_id}")

        # Make file publicly accessible
        print("\n5. Setting file permissions...")
        service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()

        print("✅ File is now publicly accessible")

        # Generate links
        drive_link = f"https://drive.google.com/file/d/{file_id}/view"
        print(f"\n📎 Drive Link: {drive_link}")

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYour Drive upload is configured correctly!")
        print(f"Videos will be uploaded to folder: {DRIVE_FOLDER_ID}")
        print(f"Check the test file at: {drive_link}")

        # Optionally delete the test file
        print("\n⚠️  Note: You can delete the test file from your Drive folder")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_drive_upload()
    exit(0 if success else 1)
