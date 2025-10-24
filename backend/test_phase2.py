"""
Phase 2 Test Script - Computer Vision Models
Tests field detection and health segmentation endpoints
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_endpoint(name, method, url, **kwargs):
    """Test an endpoint and print results"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=30, **kwargs)
        else:
            response = requests.post(url, timeout=30, **kwargs)
        
        status = "✅ PASS" if response.status_code == 200 else "❌ FAIL"
        print(f"{status} | {name}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)[:500]}...")
        else:
            print(f"   Error: {response.text[:200]}")
        
        print()
        return response.status_code == 200
    
    except Exception as e:
        print(f"❌ FAIL | {name}")
        print(f"   Error: {str(e)}")
        print()
        return False

def main():
    print("=" * 70)
    print("PHASE 2 - COMPUTER VISION MODELS TEST")
    print("=" * 70)
    print()
    
    print("⚠️  NOTE: This phase requires large dependencies (PyTorch, YOLOv8).")
    print("   Installation may take 5-10 minutes and ~2GB disk space.")
    print("   Press Ctrl+C to cancel if needed.")
    print()
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Field Detection
    print("🔍 Testing Field Detection Endpoint...")
    total_tests += 1
    if test_endpoint(
        "POST /api/detect-fields",
        "POST",
        f"{BASE_URL}/api/detect-fields?farm_id=test_farm_001"
    ):
        tests_passed += 1
    
    # Test 2: Health Segmentation
    print("🎨 Testing Health Zone Segmentation...")
    total_tests += 1
    if test_endpoint(
        "POST /api/segment-health",
        "POST",
        f"{BASE_URL}/api/segment-health?farm_id=test_farm_001&analysis_id=test_analysis_001"
    ):
        tests_passed += 1
    
    # Test 3: Get Visualizations
    print("🖼️  Testing Visualization Retrieval...")
    total_tests += 1
    if test_endpoint(
        "GET /api/analysis/test_analysis_001/visualizations",
        "GET",
        f"{BASE_URL}/api/analysis/test_analysis_001/visualizations"
    ):
        tests_passed += 1
    
    # Summary
    print("=" * 70)
    print(f"TEST RESULTS: {tests_passed}/{total_tests} tests passed")
    print("=" * 70)
    print()
    
    if tests_passed == total_tests:
        print("✅ ALL TESTS PASSED! Phase 2 computer vision models working!")
        print()
        print("📁 Check the backend/temp/ folder for generated visualizations:")
        temp_dir = Path("temp")
        if temp_dir.exists():
            files = list(temp_dir.glob("*.png"))
            for file in files:
                print(f"   - {file.name}")
        print()
        print("🚀 Ready for Phase 3: Spectral Analysis Implementation!")
    else:
        print("❌ Some tests failed.")
        print()
        print("💡 Common issues:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Ensure server is running: python main.py")
        print("   3. PyTorch installation may need specific version for your system")
    
    print()

if __name__ == "__main__":
    main()
