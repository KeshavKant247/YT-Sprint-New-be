#!/bin/bash

# Script to encode credentials.json to base64 for Vercel deployment
# Usage: ./encode_credentials.sh

echo "================================"
echo "Credentials Encoder for Vercel"
echo "================================"
echo ""

# Check if credentials.json exists
if [ ! -f "credentials.json" ]; then
    echo "❌ Error: credentials.json not found in current directory"
    echo ""
    echo "Please ensure you have:"
    echo "1. Created a Google Service Account"
    echo "2. Downloaded the JSON key file"
    echo "3. Renamed it to 'credentials.json'"
    echo "4. Placed it in the backend directory"
    echo ""
    echo "See GOOGLE_SHEETS_SETUP.md for detailed instructions"
    exit 1
fi

echo "✓ Found credentials.json"
echo ""

# Encode to base64
echo "Encoding to base64..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    BASE64_CREDS=$(base64 -i credentials.json | tr -d '\n')
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    BASE64_CREDS=$(base64 -w 0 credentials.json)
else
    echo "❌ Unsupported OS. Please encode manually."
    echo ""
    echo "On Mac/Linux:"
    echo "  base64 -i credentials.json | tr -d '\\n'"
    echo ""
    echo "On Windows PowerShell:"
    echo "  [Convert]::ToBase64String([IO.File]::ReadAllBytes(\"credentials.json\"))"
    exit 1
fi

echo "✓ Encoding complete"
echo ""

# Display results
echo "================================"
echo "Add this to Vercel:"
echo "================================"
echo ""
echo "Variable name: GOOGLE_CREDENTIALS_BASE64"
echo ""
echo "Value (copied to clipboard if available):"
echo "$BASE64_CREDS"
echo ""

# Try to copy to clipboard
if command -v pbcopy &> /dev/null; then
    # macOS
    echo "$BASE64_CREDS" | pbcopy
    echo "✓ Copied to clipboard (macOS)"
elif command -v xclip &> /dev/null; then
    # Linux with xclip
    echo "$BASE64_CREDS" | xclip -selection clipboard
    echo "✓ Copied to clipboard (Linux)"
elif command -v xsel &> /dev/null; then
    # Linux with xsel
    echo "$BASE64_CREDS" | xsel --clipboard
    echo "✓ Copied to clipboard (Linux)"
else
    echo "⚠ Could not copy to clipboard automatically"
    echo "  Please copy the value above manually"
fi

echo ""
echo "================================"
echo "Next Steps:"
echo "================================"
echo ""
echo "1. Go to https://vercel.com/dashboard"
echo "2. Select your 'shortssprits-backend' project"
echo "3. Go to Settings > Environment Variables"
echo "4. Add new variable:"
echo "   - Name: GOOGLE_CREDENTIALS_BASE64"
echo "   - Value: (paste the value above)"
echo "   - Environment: Production, Preview, Development"
echo "5. Click 'Save'"
echo "6. Redeploy your project"
echo ""
echo "See VERCEL_DEPLOYMENT_GUIDE.md for complete instructions"
echo ""
