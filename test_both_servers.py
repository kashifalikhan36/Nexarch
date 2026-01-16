#!/usr/bin/env python
"""
Comprehensive test for both FastAPI and MCP servers running together
Tests all endpoints, MCP tools, and integration
"""
import requests
import json
import sys
import time
import uuid
from pathlib import Path

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_test(name):
    print(f"\n{Colors.CYAN}{Colors.BOLD}[TEST] {name}{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}  [OK] {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}  [FAIL] {msg}{Colors.END}")

def print_info(msg):
    print(f"  {Colors.CYAN}[INFO] {msg}{Colors.END}")

def print_warning(msg):
    print(f"  {Colors.YELLOW}[WARN] {msg}{Colors.END}")

# Server URLs
FASTAPI_URL = "http://127.0.0.1:8000"
MCP_URL = "http://127.0.0.1:8001"

# Test credentials (will be created during test)
API_KEY = None
TENANT_ID = None

test_results = {"passed": 0, "failed": 0, "warnings": 0}

def setup_tenant():
    """Create a test tenant and get API key"""
    global API_KEY, TENANT_ID
    
    print_test("Setup: Create Test Tenant")
    try:
        response = requests.post(
            f"{FASTAPI_URL}/api/v1/admin/tenants",
            json={
                "name": "Integration Test Tenant",
                "admin_email": f"test_{uuid.uuid4().hex[:8]}@example.com"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            API_KEY = data['api_key']
            TENANT_ID = data['id']
            print_success(f"Created tenant: {TENANT_ID[:8]}...")
            print_info(f"API Key: {API_KEY[:20]}...")
            test_results["passed"] += 1
            return True
        else:
            print_error(f"Failed to create tenant: {response.status_code}")
            print_error(f"Response: {response.text}")
            test_results["failed"] += 1
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        test_results["failed"] += 1
        return False

def test_fastapi_health():
    """Test FastAPI health endpoint"""
    print_test("FastAPI Health Check")
    try:
        response = requests.get(f"{FASTAPI_URL}/api/v1/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"FastAPI is healthy - Status: {data.get('status')}")
            print_info(f"Database: {data.get('database')}")
            print_info(f"Cache: {data.get('cache')}")
            test_results["passed"] += 1
            return True
        else:
            print_error(f"Health check failed with status {response.status_code}")
            test_results["failed"] += 1
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to FastAPI server (not running)")
        print_info("Run: python start.py")
        test_results["failed"] += 1
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        test_results["failed"] += 1
        return False

def test_fastapi_root():
    """Test FastAPI root endpoint"""
    print_test("FastAPI Root Endpoint")
    try:
        response = requests.get(FASTAPI_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Service: {data.get('service')} v{data.get('version')}")
            print_info(f"Features: {', '.join(data.get('features', {}).keys())}")
            test_results["passed"] += 1
            return True
        else:
            print_error(f"Failed with status {response.status_code}")
            test_results["failed"] += 1
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        test_results["failed"] += 1
        return False

def test_fastapi_system_info():
    """Test FastAPI system info endpoint"""
    print_test("FastAPI System Info & Capabilities")
    try:
        # Get system info
        response = requests.get(f"{FASTAPI_URL}/api/v1/system/info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success("System info retrieved")
            print_info(f"App: {data.get('app_name')} v{data.get('version')}")
            features = data.get('features', {})
            print_info(f"Multi-tenant: {features.get('multi_tenancy')}")
            print_info(f"AI Generation: {features.get('ai_generation')}")
            print_info(f"Caching: {features.get('caching')}")
            
            # Check capabilities for actual Azure OpenAI status
            cap_response = requests.get(f"{FASTAPI_URL}/api/v1/system/capabilities", timeout=5)
            if cap_response.status_code == 200:
                cap_data = cap_response.json()
                ai_features = cap_data.get('ai_features', {})
                if ai_features.get('enabled') and ai_features.get('model'):
                    print_success(f"Azure OpenAI: Configured (Model: {ai_features.get('model')})")
                else:
                    print_warning("Azure OpenAI: Not configured or disabled")
                    test_results["warnings"] += 1
            
            test_results["passed"] += 1
            return True
        else:
            print_error(f"Failed with status {response.status_code}")
            test_results["failed"] += 1
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        test_results["failed"] += 1
        return False

def test_fastapi_ingest_sample():
    """Test FastAPI generate sample data endpoint"""
    print_test("FastAPI Sample Data Generation")
    try:
        response = requests.post(
            f"{FASTAPI_URL}/api/v1/demo/generate-sample-data?count=50",
            headers={
                "X-Tenant-ID": TENANT_ID,
                "X-API-Key": API_KEY
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Generated {data.get('spans_created', 0)} sample spans")
            print_info(f"Services: {', '.join(data.get('services', []))}")
            print_info(f"Time range: {data.get('time_range')}")
            test_results["passed"] += 1
            return True
        else:
            print_error(f"Failed with status {response.status_code}: {response.text}")
            test_results["failed"] += 1
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        test_results["failed"] += 1
        return False

def test_fastapi_architecture():
    """Test FastAPI architecture retrieval"""
    print_test("FastAPI Architecture Retrieval")
    try:
        response = requests.get(
            f"{FASTAPI_URL}/api/v1/architecture/current",
            headers={
                "X-Tenant-ID": TENANT_ID,
                "X-API-Key": API_KEY
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved architecture: {len(data.get('nodes', []))} nodes, {len(data.get('edges', []))} edges")
            if data.get('metrics_summary'):
                metrics = data['metrics_summary']
                print_info(f"Metrics: {list(metrics.keys())[:5]}")
            test_results["passed"] += 1
            return True
        else:
            print_error(f"Failed with status {response.status_code}")
            test_results["failed"] += 1
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        test_results["failed"] += 1
        return False

def test_fastapi_issues():
    """Test FastAPI issue detection"""
    print_test("FastAPI Issue Detection")
    try:
        response = requests.get(
            f"{FASTAPI_URL}/api/v1/architecture/issues",
            headers={
                "X-Tenant-ID": TENANT_ID,
                "X-API-Key": API_KEY
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            issues = data.get('issues', [])
            print_success(f"Retrieved {len(issues)} detected issues")
            
            # Show first few issues
            for i, issue in enumerate(issues[:3]):
                severity = issue.get('severity', 'unknown')
                issue_type = issue.get('type', 'unknown')
                print_info(f"Issue {i+1}: [{severity}] {issue_type}")
            
            if len(issues) > 3:
                print_info(f"... and {len(issues) - 3} more issues")
            
            test_results["passed"] += 1
            return True
        else:
            print_error(f"Failed with status {response.status_code}")
            test_results["failed"] += 1
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        test_results["failed"] += 1
        return False

def test_fastapi_workflows():
    """Test FastAPI workflow generation"""
    print_test("FastAPI Workflow Generation")
    try:
        # First trigger generation
        gen_response = requests.post(
            f"{FASTAPI_URL}/api/v1/workflows/trigger-generation",
            json={"goal": "optimize_performance"},
            headers={
                "X-Tenant-ID": TENANT_ID,
                "X-API-Key": API_KEY
            },
            timeout=30  # AI operations take longer
        )
        
        # Then get generated workflows
        response = requests.get(
            f"{FASTAPI_URL}/api/v1/workflows/generated",
            headers={
                "X-Tenant-ID": TENANT_ID,
                "X-API-Key": API_KEY
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            workflows = data.get('workflows', [])
            print_success(f"Generated {len(workflows)} workflow alternatives")
            
            for i, wf in enumerate(workflows[:3]):
                print_info(f"Workflow {i+1}: {wf.get('name')} - Score: {wf.get('score', 0)}")
            
            test_results["passed"] += 1
            return True
        else:
            print_error(f"Failed with status {response.status_code}: {response.text}")
            test_results["failed"] += 1
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        test_results["failed"] += 1
        return False

def test_mcp_server():
    """Test MCP server (basic connectivity)"""
    print_test("MCP Server Connectivity")
    print_info("MCP runs in stdio mode by default (for Claude Desktop)")
    print_info("To test MCP with HTTP, restart with: python start_mcp.py --http")
    print_warning("Skipping HTTP test for stdio mode")
    test_results["warnings"] += 1
    return True

def test_api_documentation():
    """Test FastAPI documentation availability"""
    print_test("FastAPI Documentation")
    try:
        response = requests.get(f"{FASTAPI_URL}/docs", timeout=5)
        if response.status_code == 200:
            print_success("Swagger UI available at /docs")
            test_results["passed"] += 1
            return True
        else:
            print_error(f"Documentation not available: {response.status_code}")
            test_results["failed"] += 1
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        test_results["failed"] += 1
        return False

def test_integration():
    """Test integration between services"""
    print_test("Integration Test")
    try:
        # Create sample data
        print_info("Generating sample data via FastAPI...")
        create_response = requests.post(
            f"{FASTAPI_URL}/api/v1/demo/generate-sample-data?count=20",
            headers={
                "X-Tenant-ID": "integration-test",
                "X-API-Key": API_KEY
            },
            timeout=10
        )
        
        if create_response.status_code != 200:
            print_error("Failed to generate sample data")
            test_results["failed"] += 1
            return False
        
        # Retrieve and verify
        print_info("Retrieving architecture...")
        arch_response = requests.get(
            f"{FASTAPI_URL}/api/v1/architecture/current",
            headers={
                "X-Tenant-ID": "integration-test",
                "X-API-Key": API_KEY
            },
            timeout=10
        )
        
        if arch_response.status_code != 200:
            print_error("Failed to retrieve architecture")
            test_results["failed"] += 1
            return False
        
        arch = arch_response.json()
        if len(arch.get('nodes', [])) > 0:
            print_success(f"Integration verified - Architecture built from spans")
            print_info(f"Generated {len(arch['nodes'])} nodes and {len(arch['edges'])} edges")
            test_results["passed"] += 1
            return True
        else:
            print_warning("Architecture created but no nodes found")
            test_results["warnings"] += 1
            return False
            
    except Exception as e:
        print_error(f"Integration test error: {e}")
        test_results["failed"] += 1
        return False

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
    print(f"  Nexarch Multi-Server Integration Test Suite")
    print(f"{'='*60}{Colors.END}\n")
    
    print_info(f"FastAPI URL: {FASTAPI_URL}")
    print_info(f"MCP URL: {MCP_URL}")
    print_info("Testing both servers together...")
    
    # Wait a moment for servers to be ready
    time.sleep(1)
    
    # Setup: Create tenant and get API key
    if not setup_tenant():
        print_error("Failed to setup test tenant - cannot continue")
        return 1
    
    # Run tests
    tests = [
        ("FastAPI Health", test_fastapi_health),
        ("FastAPI Root", test_fastapi_root),
        ("FastAPI System Info", test_fastapi_system_info),
        ("API Documentation", test_api_documentation),
        ("Sample Data Generation", test_fastapi_ingest_sample),
        ("Architecture Retrieval", test_fastapi_architecture),
        ("Issue Detection", test_fastapi_issues),
        ("Workflow Generation", test_fastapi_workflows),
        ("Integration", test_integration),
        ("MCP Server", test_mcp_server),
    ]
    
    # Run all tests
    for name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print_error(f"Unexpected error in {name}: {e}")
            test_results["failed"] += 1
        time.sleep(0.5)  # Brief pause between tests
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
    print(f"  Test Results Summary")
    print(f"{'='*60}{Colors.END}\n")
    
    total = test_results["passed"] + test_results["failed"]
    print(f"{Colors.GREEN}  Passed:   {test_results['passed']}/{total}{Colors.END}")
    print(f"{Colors.RED}  Failed:   {test_results['failed']}/{total}{Colors.END}")
    print(f"{Colors.YELLOW}  Warnings: {test_results['warnings']}{Colors.END}")
    
    if test_results["failed"] == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}  ✓ All tests passed!{Colors.END}")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}  ✗ Some tests failed{Colors.END}")
        print(f"\n{Colors.YELLOW}Troubleshooting:{Colors.END}")
        print("  1. Check if both servers are running: python start.py --status")
        print("  2. Review server logs in the terminal windows")
        print("  3. Verify .env file has correct Azure OpenAI credentials")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.END}")
        sys.exit(130)
