#!/bin/bash

# API Testing Script
# Tests all endpoints of the Adda Education Dashboard API

BASE_URL="http://localhost:5000"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Adda Education Dashboard - API Tests${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
echo "GET /"
response=$(curl -s $BASE_URL/)
echo "$response" | jq '.'
if echo "$response" | jq -e '.status == "running"' > /dev/null; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}✗ Health check failed${NC}"
fi
echo ""

# Test 2: Get All Data
echo -e "${YELLOW}Test 2: Get All Data${NC}"
echo "GET /api/data"
response=$(curl -s $BASE_URL/api/data)
echo "$response" | jq '.'
if echo "$response" | jq -e '.success == true' > /dev/null; then
    echo -e "${GREEN}✓ Get data passed${NC}"
else
    echo -e "${RED}✗ Get data failed${NC}"
fi
echo ""

# Test 3: Get Filters
echo -e "${YELLOW}Test 3: Get Filters${NC}"
echo "GET /api/filters"
response=$(curl -s $BASE_URL/api/filters)
echo "$response" | jq '.'
if echo "$response" | jq -e '.success == true' > /dev/null; then
    echo -e "${GREEN}✓ Get filters passed${NC}"
else
    echo -e "${RED}✗ Get filters failed${NC}"
fi
echo ""

# Test 4: Get Categories
echo -e "${YELLOW}Test 4: Get Categories${NC}"
echo "GET /api/categories"
response=$(curl -s $BASE_URL/api/categories)
echo "$response" | jq '.'
if echo "$response" | jq -e '.success == true' > /dev/null; then
    echo -e "${GREEN}✓ Get categories passed${NC}"
else
    echo -e "${RED}✗ Get categories failed${NC}"
fi
echo ""

# Test 5: Get Exams
echo -e "${YELLOW}Test 5: Get Exams${NC}"
echo "GET /api/exams"
response=$(curl -s $BASE_URL/api/exams)
echo "$response" | jq '.'
if echo "$response" | jq -e '.success == true' > /dev/null; then
    echo -e "${GREEN}✓ Get exams passed${NC}"
else
    echo -e "${RED}✗ Get exams failed${NC}"
fi
echo ""

# Test 6: Add New Entry (commented out to avoid modifying sheet during tests)
echo -e "${YELLOW}Test 6: Add New Entry (Skipped)${NC}"
echo "POST /api/add"
echo "Skipped to avoid modifying the sheet"
echo ""

# Test 7: Update Entry (commented out)
echo -e "${YELLOW}Test 7: Update Entry (Skipped)${NC}"
echo "PUT /api/update/<row_id>"
echo "Skipped to avoid modifying the sheet"
echo ""

# Test 8: Delete Entry (commented out)
echo -e "${YELLOW}Test 8: Delete Entry (Skipped)${NC}"
echo "DELETE /api/delete/<row_id>"
echo "Skipped to avoid modifying the sheet"
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}API Tests Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
