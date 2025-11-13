# Adda Education Dashboard - Backend

Flask backend for managing YouTube Shorts content using Google Sheets as a database.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google Sheets API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API and Google Drive API
4. Create a Service Account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Give it a name and click "Create"
   - Grant it "Editor" role
   - Click "Done"
5. Create credentials:
   - Click on the service account you just created
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose JSON format
   - Download the JSON file and rename it to `credentials.json`
   - Place it in the `backend` directory
6. Share your Google Sheet:
   - Open your Google Sheet
   - Click "Share"
   - Add the service account email (found in credentials.json as "client_email")
   - Give it "Editor" permissions

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` if needed to change the Sheet ID.

### 4. Run the Server

```bash
python app.py
```

The server will run on `http://localhost:5000`

## API Endpoints

- `GET /` - Health check
- `GET /api/data` - Fetch all data from sheet
- `GET /api/filters` - Get unique filter values
- `GET /api/categories` - Get predefined categories and subcategories
- `GET /api/exams` - Get exam details with subjects
- `POST /api/add` - Add new row
- `PUT /api/update/<row_id>` - Update specific row
- `DELETE /api/delete/<row_id>` - Delete specific row

## Sheet Structure

Columns:
- Sr no.
- Type of Content
- Sub category
- Subject
- Video Link
- Edit
- Editor Brief
- Final Edited Link
