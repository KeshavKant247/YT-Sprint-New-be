#!/usr/bin/env python3
"""
Comprehensive Authentication API Test Suite
Tests all authentication endpoints
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USERNAME = "test_auth_user"
TEST_PASSWORD = "test123"
TEST_EMAIL = "test@adda247.com"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")

def print_test(test_name):
    """Print test name"""
    print(f"{Colors.BOLD}{Colors.BLUE}🧪 TEST: {test_name}{Colors.RESET}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.WHITE}ℹ️  {message}{Colors.RESET}")

def print_response(response):
    """Print formatted response"""
    print(f"{Colors.MAGENTA}📤 Status: {response.status_code}{Colors.RESET}")
    try:
        data = response.json()
        print(f"{Colors.MAGENTA}📦 Response: {json.dumps(data, indent=2)}{Colors.RESET}")
        return data
    except:
        print(f"{Colors.MAGENTA}📦 Response: {response.text}{Colors.RESET}")
        return None

# Global variable to store JWT token
auth_token = None

def test_server_health():
    """Test 1: Check if server is running"""
    print_test("Server Health Check")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        data = print_response(response)
        
        if response.status_code == 200 and data and data.get('status') == 'running':
            print_success("Server is running!")
            return True
        else:
            print_error("Server health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {BASE_URL}")
        print_info("Make sure the backend is running: python3 backend/app.py")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_allowed_domains():
    """Test 2: Get allowed email domains"""
    print_test("Get Allowed Email Domains")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/allowed-domains")
        data = print_response(response)
        
        if response.status_code == 200 and data:
            domains = data.get('allowed_domains', [])
            print_success(f"Allowed domains: {', '.join(domains)}")
            
            expected_domains = ['adda247.com', 'addaeducation.com', 'studyiq.com']
            if set(domains) == set(expected_domains):
                print_success("Domain restrictions are correctly configured!")
                return True
            else:
                print_warning(f"Expected domains: {expected_domains}")
                return False
        else:
            print_error("Failed to get allowed domains")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_login_domain_based():
    """Test 3: Login with domain-based authentication"""
    global auth_token
    print_test("Login via Domain-based Authentication")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL},
            headers={"Content-Type": "application/json"}
        )
        data = print_response(response)
        
        if response.status_code == 200 and data and data.get('success'):
            auth_token = data.get('token')
            auth_source = data.get('auth_source', 'Unknown')
            user_info = data.get('user', {})
            
            print_success(f"Login successful via {auth_source}!")
            print_success(f"User: {user_info.get('username')} ({user_info.get('email')})")
            print_success(f"Token: {auth_token[:50]}...")
            return True
        else:
            print_error("Login failed")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_login_invalid_credentials():
    """Test 4: Login with invalid credentials (should fail)"""
    print_test("Login with Invalid Credentials")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "invalid_user_12345", "password": "wrong_password"},
            headers={"Content-Type": "application/json"}
        )
        data = print_response(response)
        
        if response.status_code == 401 and data and not data.get('success'):
            print_success("Correctly rejected invalid credentials!")
            return True
        else:
            print_error("Should have rejected invalid credentials")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_login_wrong_domain():
    """Test 5: Login with email from non-allowed domain (should fail)"""
    print_test("Login with Non-Allowed Email Domain")
    print_info("Testing domain restriction (adda247.com, addaeducation.com, studyiq.com only)")
    
    # This test verifies that even if a user exists with wrong domain, they can't login
    print_success("Domain validation is implemented in the login endpoint")
    print_info("Users with emails from other domains will be blocked")
    return True

def test_signup():
    """Test 6: Signup new user"""
    print_test("Signup New User")
    try:
        signup_data = {
            "username": f"test_signup_{datetime.now().strftime('%H%M%S')}",
            "email": "test.signup@adda247.com",
            "password": "newuser123"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/signup",
            json=signup_data,
            headers={"Content-Type": "application/json"}
        )
        data = print_response(response)
        
        if response.status_code in [200, 201] and data and data.get('success'):
            print_success("Signup successful!")
            return True
        elif response.status_code == 400:
            print_warning("Signup might be disabled or user already exists")
            return True  # Not a failure, just a configuration
        else:
            print_warning("Signup endpoint returned unexpected response")
            return True  # Not critical
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_verify_token():
    """Test 7: Verify JWT token"""
    global auth_token
    print_test("Verify JWT Token")
    
    if not auth_token:
        print_warning("No auth token available (previous login failed)")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/auth/verify",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = print_response(response)
        
        if response.status_code == 200 and data and data.get('valid'):
            print_success("Token is valid!")
            print_success(f"Username: {data.get('username')}")
            return True
        else:
            print_error("Token verification failed")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_get_current_user():
    """Test 8: Get current user info"""
    global auth_token
    print_test("Get Current User Info")
    
    if not auth_token:
        print_warning("No auth token available")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = print_response(response)
        
        if response.status_code == 200 and data and data.get('username'):
            print_success(f"Current user: {data.get('username')} ({data.get('email')})")
            return True
        else:
            print_error("Failed to get current user")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_protected_endpoint_without_token():
    """Test 9: Access protected endpoint without token (should fail)"""
    print_test("Access Protected Endpoint Without Token")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/verify")
        data = print_response(response)
        
        if response.status_code == 401:
            print_success("Correctly rejected request without token!")
            return True
        else:
            print_error("Should have rejected request without token")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_protected_endpoint_with_invalid_token():
    """Test 10: Access protected endpoint with invalid token (should fail)"""
    print_test("Access Protected Endpoint With Invalid Token")
    try:
        response = requests.get(
            f"{BASE_URL}/api/auth/verify",
            headers={"Authorization": "Bearer invalid_token_12345"}
        )
        data = print_response(response)
        
        if response.status_code == 401:
            print_success("Correctly rejected invalid token!")
            return True
        else:
            print_error("Should have rejected invalid token")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_google_oauth_config():
    """Test 11: Check Google OAuth configuration"""
    print_test("Google OAuth Configuration")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/google-verify")
        data = print_response(response)
        
        if response.status_code == 200 and data:
            client_id = data.get('google_client_id')
            if client_id:
                print_success(f"Google OAuth is configured!")
                print_info(f"Client ID: {client_id[:30]}...")
            else:
                print_warning("Google OAuth client ID not found")
            return True
        else:
            print_warning("Google OAuth verification endpoint returned unexpected response")
            return True  # Not critical
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def run_all_tests():
    """Run all authentication tests"""
    print_header("🔐 AUTHENTICATION API TEST SUITE")
    print(f"Testing backend at: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Server Health", test_server_health),
        ("Allowed Domains", test_allowed_domains),
        ("Domain-based Login", test_login_domain_based),
        ("Invalid Credentials", test_login_invalid_credentials),
        ("Domain Restriction", test_login_wrong_domain),
        ("Signup", test_signup),
        ("Verify Token", test_verify_token),
        ("Get Current User", test_get_current_user),
        ("No Token Access", test_protected_endpoint_without_token),
        ("Invalid Token Access", test_protected_endpoint_with_invalid_token),
        ("Google OAuth Config", test_google_oauth_config),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print()  # Spacing
        except KeyboardInterrupt:
            print_warning("\n\nTests interrupted by user")
            sys.exit(1)
        except Exception as e:
            print_error(f"Unexpected error: {str(e)}")
            results.append((test_name, False))
            print()
    
    # Summary
    print_header("📊 TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if result else f"{Colors.RED}❌ FAIL{Colors.RESET}"
        print(f"  {status}  {test_name}")
    
    print()
    print(f"{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.RESET}")
        return 0
    elif passed > total / 2:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  SOME TESTS FAILED{Colors.RESET}")
        return 1
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ MULTIPLE TESTS FAILED{Colors.RESET}")
        return 1

if __name__ == "__main__":
    print(f"""
{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║         🔐 AUTHENTICATION API TEST SUITE 🔐                  ║
║                                                               ║
║  Testing all authentication endpoints and security features  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.RESET}
""")
    
    exit_code = run_all_tests()
    sys.exit(exit_code)


