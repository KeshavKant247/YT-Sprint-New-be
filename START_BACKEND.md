# How to Start/Restart the Backend Server

## Current Issue
You're getting a 403 error because the backend server is running with old code that doesn't have write access to Google Sheets.

## Solution: Restart the Backend

### Step 1: Stop the Current Backend

Find the running Flask process and kill it:

```bash
# Find the Flask process
lsof -ti:5000 | xargs kill -9

# Or manually:
ps aux | grep python
# Then kill the process ID: kill -9 <PID>
```

### Step 2: Start the Backend with New Code

```bash
# Navigate to backend folder
cd /Users/adda247/Desktop/shortssprints/backend

# Make sure all dependencies are installed
pip3 install -r requirements.txt

# Start the Flask server
python3 app.py
```

You should see:
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

### Step 3: Test the Connection

Keep the backend running and in a new terminal:

```bash
cd /Users/adda247/Desktop/shortssprints/backend

# Test add endpoint
curl -X POST http://localhost:5000/api/add \
  -H "Content-Type: application/json" \
  -d '{
    "Sr no.": "999",
    "Exam Name": "Test",
    "Subject": "Test",
    "Type of Content": "Content",
    "Sub category": "Tips & Tricks",
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

### Step 4: Test in Frontend

1. Make sure backend is running (Step 2)
2. Refresh your frontend page
3. Try adding an entry again
4. It should work now! ✅

## Quick Commands

### Kill backend:
```bash
lsof -ti:5000 | xargs kill -9
```

### Start backend:
```bash
cd /Users/adda247/Desktop/shortssprints/backend && python3 app.py
```

### Check if backend is running:
```bash
curl http://localhost:5000/health
```

## Common Issues

### Port 5000 already in use
```bash
# Kill whatever is using port 5000
lsof -ti:5000 | xargs kill -9

# Then start backend again
python3 app.py
```

### "Module not found" errors
```bash
# Install dependencies
pip3 install -r requirements.txt
```

### Frontend can't connect to backend
- Check backend is running: `curl http://localhost:5000/health`
- Check backend URL in frontend code
- Check CORS is enabled (already done in app.py)

## Verify Setup is Working

Run the test script:
```bash
cd /Users/adda247/Desktop/shortssprints/backend
python3 test_setup.py
```

You should see: `✅ SETUP IS CORRECT - Backend should work!`

---

**Your setup is already correct!** You just need to restart the backend server.
