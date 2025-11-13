#!/usr/bin/env python3
"""Quick test to verify the endpoints return valid JSON"""
import json
from app import app

def test_endpoint(endpoint_name, url):
    """Test an endpoint and print results"""
    with app.test_client() as client:
        response = client.get(url)
        print(f"\n{'='*60}")
        print(f"Testing: {endpoint_name}")
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ SUCCESS - Response contains {len(str(data))} characters")
            if 'success' in data:
                print(f"   Success field: {data['success']}")
            if 'exams' in data:
                print(f"   Exams count: {len(data['exams'])}")
            if 'categories' in data:
                print(f"   Categories count: {len(data['categories'])}")
        else:
            print(f"❌ FAILED")
            print(f"   Response: {response.get_data(as_text=True)[:200]}")

if __name__ == '__main__':
    print("Testing API Endpoints Locally")
    print("="*60)
    
    # Test the three failing endpoints
    test_endpoint("/api/categories", "/api/categories")
    test_endpoint("/api/exams", "/api/exams")
    test_endpoint("/api/health", "/api/health")
    
    print(f"\n{'='*60}")
    print("✅ All static endpoints tested!")
    print("Note: /api/data requires Google credentials")
    print("="*60)


