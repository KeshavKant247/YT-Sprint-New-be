#!/bin/bash
# Test Domain-Based Login (No Password Required)

echo "========================================"
echo "🔐 Testing Domain-Based Authentication"
echo "========================================"
echo ""

BASE_URL="http://localhost:5000"

# Test 1: Valid domain (adda247.com)
echo "Test 1: Login with adda247.com email ✅"
curl -s -X POST ${BASE_URL}/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@adda247.com"}' | jq '.'
echo ""
echo "----------------------------------------"
echo ""

# Test 2: Valid domain (addaeducation.com)
echo "Test 2: Login with addaeducation.com email ✅"
curl -s -X POST ${BASE_URL}/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"jane@addaeducation.com"}' | jq '.'
echo ""
echo "----------------------------------------"
echo ""

# Test 3: Valid domain (studyiq.com)
echo "Test 3: Login with studyiq.com email ✅"
curl -s -X POST ${BASE_URL}/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@studyiq.com"}' | jq '.'
echo ""
echo "----------------------------------------"
echo ""

# Test 4: Invalid domain (gmail.com) - should fail
echo "Test 4: Login with gmail.com email ❌ (Should FAIL)"
curl -s -X POST ${BASE_URL}/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"hacker@gmail.com"}' | jq '.'
echo ""
echo "----------------------------------------"
echo ""

# Test 5: Invalid email format
echo "Test 5: Invalid email format ❌ (Should FAIL)"
curl -s -X POST ${BASE_URL}/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"notanemail"}' | jq '.'
echo ""
echo "----------------------------------------"
echo ""

# Test 6: Empty email
echo "Test 6: Empty email ❌ (Should FAIL)"
curl -s -X POST ${BASE_URL}/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":""}' | jq '.'
echo ""
echo "========================================"
echo "✅ Testing Complete!"
echo "========================================"


