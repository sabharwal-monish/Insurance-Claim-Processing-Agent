"""
Test script for the Insurance Claim Processing Agent webhook
Tests the Dialogflow webhook endpoint with mock payloads
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Mock Dialogflow payload for policy number intent
MOCK_PAYLOAD_POLICY = {
    "session": "projects/test-project/agent/sessions/test-session-12345",
    "queryResult": {
        "queryText": "My policy number is ABC-12345",
        "intent": {
            "displayName": "provide_policy_number"
        },
        "parameters": {
            "policy_number": "ABC-12345"
        }
    }
}

# Mock Dialogflow payload for name intent
MOCK_PAYLOAD_NAME = {
    "session": "projects/test-project/agent/sessions/test-session-12345",
    "queryResult": {
        "queryText": "My name is John Doe",
        "intent": {
            "displayName": "provide_name"
        },
        "parameters": {
            "claimant_name": "John Doe"
        }
    }
}

# Mock Dialogflow payload for incident description
MOCK_PAYLOAD_INCIDENT = {
    "session": "projects/test-project/agent/sessions/test-session-12345",
    "queryResult": {
        "queryText": "I was rear-ended at a red light",
        "intent": {
            "displayName": "describe_incident"
        },
        "parameters": {}
    }
}

def test_health_check():
    """Test the health check endpoint"""
    print("\n🔍 Testing Health Check Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_db_check():
    """Test the database connection endpoint"""
    print("\n🔍 Testing Database Connection Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/check-db")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200 and response.json().get("status") == "success"
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def test_webhook(payload, test_name):
    """Test the webhook endpoint with a mock payload"""
    print(f"\n🔍 Testing Webhook: {test_name}...")
    try:
        response = requests.post(
            f"{BASE_URL}/webhook",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("Insurance Claim Processing Agent - Webhook Tests")
    print("=" * 60)
    
    results = []
    
    # Test 1: Health Check
    results.append(("Health Check", test_health_check()))
    
    # Test 2: Database Connection
    results.append(("Database Connection", test_db_check()))
    
    # Test 3: Webhook - Policy Number
    results.append(("Webhook - Policy Number", test_webhook(MOCK_PAYLOAD_POLICY, "Policy Number")))
    
    # Test 4: Webhook - Name
    results.append(("Webhook - Name", test_webhook(MOCK_PAYLOAD_NAME, "Claimant Name")))
    
    # Test 5: Webhook - Incident Description
    results.append(("Webhook - Incident", test_webhook(MOCK_PAYLOAD_INCIDENT, "Incident Description")))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    print("=" * 60)

if __name__ == "__main__":
    main()
