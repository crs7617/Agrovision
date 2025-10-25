"""
Phase 5 Test Suite: Conversational Chat Interface
Tests chat functionality, intent detection, entity extraction, and response generation
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.chat_service import (
    parse_farmer_query,
    build_context_for_llm,
    generate_response,
    save_chat,
    get_chat_history,
    _generate_rule_based_response
)

# ANSI color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_test_header(test_name: str):
    """Print formatted test header"""
    print(f"\n{'='*60}")
    print(f"{BLUE}Testing: {test_name}{RESET}")
    print(f"{'='*60}")


def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result with color"""
    status = f"{GREEN}✓ PASSED{RESET}" if passed else f"{RED}✗ FAILED{RESET}"
    print(f"\n{test_name}: {status}")
    if details:
        print(f"  {details}")


async def test_intent_detection():
    """Test 1: Intent Detection"""
    print_test_header("Intent Detection")
    
    test_cases = [
        ("How is my wheat crop doing?", "health_check"),
        ("What fertilizer should I use?", "recommendation"),
        ("My plants are turning yellow", "problem_diagnosis"),
        ("Tell me about wheat farming", "general_info"),
        ("What's the weather forecast?", "weather"),
    ]
    
    all_passed = True
    for message, expected_intent in test_cases:
        result = parse_farmer_query(message)
        passed = result["intent"] == expected_intent
        all_passed = all_passed and passed
        
        status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        print(f"{status} '{message}' → {result['intent']} (expected: {expected_intent})")
    
    print_result("Intent Detection", all_passed)
    return all_passed


async def test_entity_extraction():
    """Test 2: Entity Extraction"""
    print_test_header("Entity Extraction")
    
    test_cases = [
        ("How is my wheat crop doing?", "wheat"),
        ("Rice paddy looks sick", "rice"),
        ("Corn plants are yellowing", "corn"),
        ("Cotton crop needs help", "cotton"),
    ]
    
    all_passed = True
    for message, expected_crop in test_cases:
        result = parse_farmer_query(message)
        detected_crop = result["entities"].get("crop_type")
        passed = detected_crop == expected_crop
        all_passed = all_passed and passed
        
        status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        print(f"{status} '{message}' → crop_type={detected_crop} (expected: {expected_crop})")
    
    print_result("Entity Extraction", all_passed)
    return all_passed


async def test_date_extraction():
    """Test 3: Date Reference Extraction"""
    print_test_header("Date Reference Extraction")
    
    test_cases = [
        ("How was my crop yesterday?", True),
        ("What happened last week?", True),
        ("Current status of field?", False),
    ]
    
    all_passed = True
    for message, should_have_date in test_cases:
        result = parse_farmer_query(message)
        has_date = "date" in result["entities"]
        passed = has_date == should_have_date
        all_passed = all_passed and passed
        
        date_ref = result["entities"].get("date", "none")
        status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        print(f"{status} '{message}' → date={date_ref}")
    
    print_result("Date Reference Extraction", all_passed)
    return all_passed


async def test_context_building():
    """Test 4: Context Building for LLM"""
    print_test_header("Context Building")
    
    # Mock data
    farm_id = "test_farm_123"
    intent = "health_check"
    entities = {"crop_type": "wheat"}
    
    latest_analysis = {
        "NDVI": 0.72,
        "EVI": 0.58,
        "health_score": 75,
        "issues": []
    }
    
    weather_data = {
        "temperature": 28,
        "humidity": 65,
        "rainfall": 0,
        "description": "Clear sky"
    }
    
    historical_trends = [
        {"value": 0.70, "date": "2024-01-01"},
        {"value": 0.72, "date": "2024-01-08"},
    ]
    
    context = build_context_for_llm(
        farm_id,
        intent,
        entities,
        latest_analysis,
        weather_data,
        historical_trends
    )
    
    # Check if key information is included
    checks = {
        "Farm ID included": farm_id in context,
        "Crop type included": "wheat" in context.lower(),
        "NDVI included": "0.72" in context,
        "Health score included": "75" in context,
        "Temperature included": "28" in context,
        "Weather description included": "clear sky" in context.lower(),
    }
    
    all_passed = all(checks.values())
    
    for check, result in checks.items():
        status = f"{GREEN}✓{RESET}" if result else f"{RED}✗{RESET}"
        print(f"{status} {check}")
    
    print(f"\n{YELLOW}Context length: {len(context)} characters{RESET}")
    
    print_result("Context Building", all_passed)
    return all_passed


async def test_llm_response_generation():
    """Test 5: LLM Response Generation"""
    print_test_header("LLM Response Generation")
    
    message = "How is my wheat crop doing?"
    context = """
    Farm ID: test_farm_123
    Crop Type: Wheat (optimal NDVI: 0.6-0.8)
    Latest Crop Health Analysis:
    - NDVI: 0.72
    - Health Score: 75/100
    Current Weather: 28°C, Humidity 65%, Clear sky
    """
    
    intent = "health_check"
    entities = {"crop_type": "wheat"}
    
    try:
        response = generate_response(message, context, intent, entities)
        
        checks = {
            "Response generated": len(response["response_text"]) > 0,
            "Has response text": "response_text" in response,
            "Has suggestions": "suggestions" in response,
            "Has confidence level": "confidence_level" in response,
            "Has source": "source" in response,
        }
        
        all_passed = all(checks.values())
        
        for check, result in checks.items():
            status = f"{GREEN}✓{RESET}" if result else f"{RED}✗{RESET}"
            print(f"{status} {check}")
        
        print(f"\n{YELLOW}Response preview:{RESET}")
        print(f"{response['response_text'][:200]}...")
        print(f"\n{YELLOW}Suggestions: {len(response['suggestions'])}{RESET}")
        for i, suggestion in enumerate(response['suggestions'][:3], 1):
            print(f"  {i}. {suggestion}")
        
        print(f"\n{YELLOW}Source: {response['source']}{RESET}")
        
        print_result("LLM Response Generation", all_passed)
        return all_passed
        
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")
        print_result("LLM Response Generation", False, str(e))
        return False


async def test_rule_based_fallback():
    """Test 6: Rule-Based Fallback Responses"""
    print_test_header("Rule-Based Fallback")
    
    test_cases = [
        ("How is my crop?", "Health Score: 75/100", "health_check", {"crop_type": "wheat"}),
        ("What should I do?", "", "recommendation", {"crop_type": "rice"}),
        ("Plants yellowing", "", "problem_diagnosis", {"crop_type": "wheat"}),
        ("What's the weather?", "Temperature: 30°C", "weather", {}),
        ("Tell me about farming", "", "general_info", {}),
    ]
    
    all_passed = True
    
    for query, context, intent, entities in test_cases:
        try:
            response = _generate_rule_based_response(query, context, intent, entities)
            
            passed = (
                len(response["response_text"]) > 0 and
                "suggestions" in response
            )
            
            all_passed = all_passed and passed
            
            status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
            print(f"{status} Intent '{intent}' → {len(response['response_text'])} chars, {len(response['suggestions'])} suggestions")
            
        except Exception as e:
            print(f"{RED}✗ Intent '{intent}' failed: {e}{RESET}")
            all_passed = False
    
    print_result("Rule-Based Fallback", all_passed)
    return all_passed


async def test_save_chat():
    """Test 7: Save Chat to Database"""
    print_test_header("Save Chat")
    
    user_id = "test_user_123"
    farm_id = "test_farm_456"
    message = "How is my wheat crop?"
    
    response = {
        "response_text": "Your wheat crop is doing well with NDVI of 0.72.",
        "suggestions": ["Monitor regularly", "Check for pests"],
        "confidence_level": "high",
        "source": "test"
    }
    
    intent = "health_check"
    entities = {"crop_type": "wheat"}
    
    try:
        chat_record = save_chat(user_id, farm_id, message, response, intent, entities)
        
        checks = {
            "Record created": chat_record is not None,
            "Has ID": "id" in chat_record,
            "Has timestamp": "timestamp" in chat_record,
            "User ID correct": chat_record.get("user_id") == user_id,
            "Farm ID correct": chat_record.get("farm_id") == farm_id,
            "Message saved": chat_record.get("message") == message,
            "Intent saved": chat_record.get("intent") == intent,
        }
        
        all_passed = all(checks.values())
        
        for check, result in checks.items():
            status = f"{GREEN}✓{RESET}" if result else f"{RED}✗{RESET}"
            print(f"{status} {check}")
        
        print(f"\n{YELLOW}Chat ID: {chat_record.get('id')}{RESET}")
        print(f"{YELLOW}Timestamp: {chat_record.get('timestamp')}{RESET}")
        
        print_result("Save Chat", all_passed)
        return all_passed
        
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")
        print_result("Save Chat", False, str(e))
        return False


async def test_get_chat_history():
    """Test 8: Get Chat History"""
    print_test_header("Get Chat History")
    
    farm_id = "test_farm_123"
    
    try:
        history = get_chat_history(farm_id, limit=10)
        
        checks = {
            "History retrieved": history is not None,
            "Is list": isinstance(history, list),
            "Has records": len(history) > 0,
        }
        
        if len(history) > 0:
            first_record = history[0]
            checks["Has message"] = "message" in first_record
            checks["Has response"] = "response_text" in first_record
            checks["Has timestamp"] = "timestamp" in first_record
        
        all_passed = all(checks.values())
        
        for check, result in checks.items():
            status = f"{GREEN}✓{RESET}" if result else f"{RED}✗{RESET}"
            print(f"{status} {check}")
        
        print(f"\n{YELLOW}Retrieved {len(history)} chat records{RESET}")
        
        print_result("Get Chat History", all_passed)
        return all_passed
        
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")
        print_result("Get Chat History", False, str(e))
        return False


async def run_all_tests():
    """Run all Phase 5 tests"""
    print(f"\n{BLUE}{'='*60}")
    print(f"PHASE 5: CONVERSATIONAL CHAT INTERFACE - TEST SUITE")
    print(f"{'='*60}{RESET}\n")
    
    tests = [
        ("Intent Detection", test_intent_detection),
        ("Entity Extraction", test_entity_extraction),
        ("Date Reference Extraction", test_date_extraction),
        ("Context Building", test_context_building),
        ("LLM Response Generation", test_llm_response_generation),
        ("Rule-Based Fallback", test_rule_based_fallback),
        ("Save Chat", test_save_chat),
        ("Get Chat History", test_get_chat_history),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n{RED}Test '{test_name}' crashed: {e}{RESET}")
            results.append((test_name, False))
    
    # Print summary
    print(f"\n{BLUE}{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}{RESET}\n")
    
    passed_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for test_name, result in results:
        status = f"{GREEN}✓ PASSED{RESET}" if result else f"{RED}✗ FAILED{RESET}"
        print(f"{status} - {test_name}")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    
    if passed_count == total_count:
        print(f"{GREEN}ALL TESTS PASSED! ({passed_count}/{total_count}){RESET}")
        print(f"{GREEN}🎉 Phase 5 Conversational Chat Interface is working!{RESET}")
    else:
        print(f"{YELLOW}TESTS PASSED: {passed_count}/{total_count}{RESET}")
        print(f"{RED}Some tests failed. Please review the output above.{RESET}")
    
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    return passed_count == total_count


if __name__ == "__main__":
    asyncio.run(run_all_tests())
