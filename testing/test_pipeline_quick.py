"""
Quick test to verify pipeline endpoint works correctly
"""
import requests
import json
import sys
import time
import subprocess
import os
from pathlib import Path

# Configuration
BACKEND_DIR = Path(__file__).parent / "backend"
BASE_URL = "http://127.0.0.1:5001/api"
ENDPOINT = f"{BASE_URL}/pipeline/generate-recipe"

def test_pipeline():
    """Test the pipeline endpoint with a simple request"""
    
    # Try simple GET on health check first
    try:
        response = requests.get(f"{BASE_URL.rsplit('/api', 1)[0]}/", timeout=2)
        print(f"✅ Flask server is responding")
    except requests.ConnectionError:
        print(f"❌ Flask server not responding at {BASE_URL}")
        print(f"   Start the server with: cd backend && python app.py")
        return False

    # Test pipeline endpoint
    payload = {
        "ingredients": ["chicken", "rice", "garlic", "soy sauce"],
        "budget": 12.00
    }

    print(f"\n📤 Sending request to: POST {ENDPOINT}")
    print(f"   Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(ENDPOINT, json=payload, timeout=5)
        
        print(f"\n📥 Response ({response.status_code}):")
        data = response.json()
        
        # Pretty print response
        print(json.dumps(data, indent=2))

        # Check response structure
        required_fields = [
            "success", "recipe", "validation", 
            "budget_check", "pipeline_status", "iterations", "timestamp"
        ]
        
        print(f"\n✅ Response validation:")
        all_present = True
        for field in required_fields:
            if field in data:
                print(f"   ✓ {field}")
            else:
                print(f"   ✗ {field} (MISSING)")
                all_present = False

        if all_present:
            print(f"\n✅ SUCCESS: Pipeline endpoint works correctly!")
            print(f"   - Status: {data['pipeline_status']}")
            print(f"   - Recipe: {data['recipe'].get('name')}")
            print(f"   - Iterations: {data['iterations']}")
            return True
        else:
            print(f"\n⚠️  Response missing required fields")
            return False

    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Connection error: {e}")
        print(f"   Make sure Flask server is running: cd backend && python app.py")
        return False
    except requests.exceptions.Timeout as e:
        print(f"\n❌ Request timeout: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"\n❌ Response is not valid JSON: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 BudgetBite Pipeline Endpoint Test")
    print("="*70)
    
    success = test_pipeline()
    
    print("\n" + "="*70)
    if success:
        print("✅ Pipeline is working correctly!")
    else:
        print("❌ Pipeline test failed - see errors above")
        sys.exit(1)
