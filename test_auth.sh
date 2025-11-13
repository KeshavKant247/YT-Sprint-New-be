#!/bin/bash

# Test Authentication Endpoints
# This script tests the signup and login endpoints

BASE_URL="http://localhost:5000"

echo "================================"
echo "Testing Authentication Endpoints"
echo "================================"
echo ""

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s -X GET "$BASE_URL/health" | python3 -m json.tool
echo ""
echo ""

# Test 2: Signup (will fail without credentials.json)
echo "2. Testing Signup..."
echo "Request:"
echo '{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "password123",
  "confirmPassword": "password123"
}'
echo ""
echo "Response:"
curl -s -X POST "$BASE_URL/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "password123",
    "confirmPassword": "password123"
  }' | python3 -m json.tool
echo ""
echo ""

# Test 3: Login (requires manual setup in sheet first)
echo "3. Testing Login..."
echo "Note: This will only work if you have manually added a user to the sheet"
echo "For testing, add this to your Google Sheet:"
echo "Username: testuser"
echo "Email: test@example.com"
echo "Password Hash: \$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYCxrqrXXqG"
echo ""
echo "Request:"
echo '{
  "username": "testuser",
  "password": "password123"
}'
echo ""
echo "Response:"
RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }')
echo "$RESPONSE" | python3 -m json.tool
echo ""

# Extract token if login was successful
TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)

if [ ! -z "$TOKEN" ]; then
  echo ""
  echo "4. Testing Token Verification..."
  echo "Token: $TOKEN"
  echo ""
  echo "Response:"
  curl -s -X GET "$BASE_URL/api/auth/verify" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
  echo ""
  echo ""

  echo "5. Testing Get Current User..."
  echo "Response:"
  curl -s -X GET "$BASE_URL/api/auth/me" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
  echo ""
else
  echo ""
  echo "Login failed - skipping token tests"
  echo "To test login, manually add a user to your Google Sheet:"
  echo "  Username: testuser"
  echo "  Email: test@example.com"
  echo "  New Password: \$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYCxrqrXXqG"
  echo "  Confirm Password: (same as New Password)"
  echo ""
  echo "Then test login with:"
  echo "  Username: testuser"
  echo "  Password: password123"
fi

echo ""
echo "================================"
echo "Testing Complete"
echo "================================"
