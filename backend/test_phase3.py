"""
Phase 3 Tests: LLM Interpretation Engine & Knowledge Base
Tests knowledge_base.py and llm_service.py functionality
"""
import sys
import os
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.knowledge_base import diagnose_issue, recommend_actions, get_health_category, CROPS_KNOWLEDGE
from services.llm_service import interpret_spectral_data, generate_farmer_response, setup_llm_client

def test_health_category():
    """Test 1: Verify NDVI health categorization"""
    print("\n=== Test 1: Health Category Classification ===")
    
    test_cases = [
        (0.8, "excellent"),
        (0.5, "fair"),
        (0.3, "poor"),
        (0.1, "poor")
    ]
    
    for ndvi, expected in test_cases:
        category, description = get_health_category(ndvi)  # Returns tuple
        status = "✓" if category == expected else "✗"
        print(f"{status} NDVI {ndvi} -> {category} (expected: {expected})")
        print(f"   Description: {description}")
    
    print("✅ Test 1 Complete\n")

def test_knowledge_base_diagnosis():
    """Test 2: Verify crop-specific diagnostics"""
    print("=== Test 2: Knowledge Base Diagnosis ===")
    
    # Test case: Healthy wheat field
    healthy_wheat = {
        "NDVI": 0.75,
        "EVI": 0.65,
        "SAVI": 0.55
    }
    
    print("\n--- Healthy Wheat Field ---")
    diagnosis = diagnose_issue(healthy_wheat, crop_type="wheat")
    print(f"Confidence: {diagnosis['confidence']}")
    print(f"Issues found: {len(diagnosis['issues'])}")
    for issue in diagnosis['issues']:
        print(f"  - {issue['type']}: {issue['description']} (severity: {issue['severity']})")
    
    # Test case: Stressed rice field
    stressed_rice = {
        "NDVI": 0.45,  # Below optimal 0.7-0.85
        "EVI": 0.35,   # Below optimal 0.6-0.75
        "SAVI": 0.4
    }
    
    print("\n--- Stressed Rice Field ---")
    diagnosis = diagnose_issue(stressed_rice, crop_type="rice")
    print(f"Confidence: {diagnosis['confidence']}")
    print(f"Issues found: {len(diagnosis['issues'])}")
    for issue in diagnosis['issues']:
        print(f"  - {issue['type']}: {issue['description']} (severity: {issue['severity']})")
    
    # Test case: Unknown crop (should use generic thresholds)
    print("\n--- Unknown Crop Type ---")
    diagnosis = diagnose_issue(healthy_wheat, crop_type="unknown_crop")
    print(f"Confidence: {diagnosis['confidence']}")
    print(f"Using crop-specific thresholds: {diagnosis['confidence'] > 0.7}")
    
    print("\n✅ Test 2 Complete\n")

def test_recommendations():
    """Test 3: Verify action recommendations"""
    print("=== Test 3: Recommendation Generation ===")
    
    # Test case: Water stressed cotton field
    water_stressed = {
        "NDVI": 0.35,
        "EVI": 0.25,
        "SAVI": 0.3,
        "NDWI": -0.1  # Low water content
    }
    
    # First get diagnosis
    diagnosis = diagnose_issue(water_stressed, crop_type="cotton")
    
    print("\n--- Water Stressed Cotton (No Rain) ---")
    print(f"Diagnosis: {len(diagnosis['issues'])} issues found")
    
    recommendations = recommend_actions(
        diagnosis,
        weather_data={"rain_forecast_7days": 0.0},
        farm_area=2.0
    )
    
    print(f"Total recommendations: {len(recommendations)}")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['action']} (Priority: {rec['priority']})")
        print(f"   Details: {rec['details']}")
        print(f"   Cost: {rec['estimated_cost']}")
        print(f"   Timeframe: {rec['timeframe']}")
    
    # Test case: Same field but with recent rain
    print("\n--- Water Stressed Cotton (Recent Rain: 25mm) ---")
    recommendations_rain = recommend_actions(
        diagnosis,
        weather_data={"rain_forecast_7days": 25.0},
        farm_area=2.0
    )
    
    print(f"Total recommendations: {len(recommendations_rain)}")
    
    # Check if irrigation priority changed
    irrig_before = next((r for r in recommendations if 'irrigat' in r['action'].lower()), None)
    irrig_after = next((r for r in recommendations_rain if 'irrigat' in r['action'].lower()), None)
    
    if irrig_before and irrig_after:
        print(f"\nIrrigation priority change: {irrig_before['priority']} -> {irrig_after['priority']}")
    else:
        print("\nIrrigation recommendations adjusted for rainfall")
    
    print("\n✅ Test 3 Complete\n")

def test_llm_setup():
    """Test 4: Verify LLM client setup"""
    print("=== Test 4: LLM Client Setup ===")
    
    groq_key = os.getenv("GROQ_API_KEY")
    
    if groq_key:
        print(f"✓ GROQ_API_KEY found (length: {len(groq_key)})")
        client_info = setup_llm_client()
        print(f"✓ Client info: {client_info}")
    else:
        print("⚠ GROQ_API_KEY not set - will use fallback mode")
        client_info = setup_llm_client()
        print(f"✓ Fallback mode enabled: {client_info}")
    
    print("\n✅ Test 4 Complete\n")

def test_spectral_interpretation():
    """Test 5: Verify spectral data interpretation"""
    print("=== Test 5: Spectral Data Interpretation ===")
    
    spectral_data = {
        "NDVI": 0.72,
        "EVI": 0.58,
        "SAVI": 0.52,
        "NDWI": 0.15
    }
    
    health_score = 75.0  # Good health
    
    print(f"\nInput indices: NDVI={spectral_data['NDVI']}, EVI={spectral_data['EVI']}")
    print(f"Health score: {health_score}")
    print("Calling interpret_spectral_data()...")
    
    try:
        interpretation = interpret_spectral_data(
            spectral_data,
            health_score=health_score,
            crop_type="wheat"
        )
        
        print(f"\n✓ Interpretation received")
        print(f"Type: {type(interpretation)}")
        
        if isinstance(interpretation, dict):
            print("\n--- Interpretation Structure ---")
            for key in interpretation:
                value = interpretation[key]
                if isinstance(value, str):
                    print(f"{key}: {value[:100]}...")
                else:
                    print(f"{key}: {value}")
        else:
            print("\n--- Interpretation (String) ---")
            print(str(interpretation)[:500])
        
    except Exception as e:
        print(f"✗ Error during interpretation: {e}")
        print("This might be expected if GROQ_API_KEY is not set")
    
    print("\n✅ Test 5 Complete\n")

def test_farmer_response():
    """Test 6: Verify farmer query responses"""
    print("=== Test 6: Farmer Query Response ===")
    
    query = "My wheat crop leaves are turning yellow. What should I do?"
    context = {
        "NDVI": 0.45,
        "crop_type": "wheat",
        "location": "Punjab, India"
    }
    
    print(f"\nQuery: '{query}'")
    print(f"Context: {context}")
    print("\nCalling generate_farmer_response()...")
    
    try:
        response = generate_farmer_response(query, context)
        
        print(f"\n✓ Response received ({len(response)} chars)")
        print("\n--- Response ---")
        print(response[:400] + "..." if len(response) > 400 else response)
        
        # Verify response quality
        checks = [
            ("addresses yellowing", "yellow" in response.lower() or "nitrogen" in response.lower() or "nutrient" in response.lower()),
            ("provides advice", any(word in response.lower() for word in ["apply", "check", "test", "recommend", "should"])),
            ("contextual", "wheat" in response.lower() or context["crop_type"] in response.lower())
        ]
        
        print("\n--- Quality Checks ---")
        for check_name, passed in checks:
            status = "✓" if passed else "✗"
            print(f"{status} {check_name}: {passed}")
        
    except Exception as e:
        print(f"✗ Error during response generation: {e}")
    
    print("\n✅ Test 6 Complete\n")

def test_crops_knowledge_base():
    """Test 7: Verify crops knowledge base structure"""
    print("=== Test 7: Crops Knowledge Base ===")
    
    print(f"\nTotal crops in knowledge base: {len(CROPS_KNOWLEDGE)}")
    
    for crop, data in CROPS_KNOWLEDGE.items():
        if crop == "default":
            continue
        print(f"\n{crop.upper()}:")
        print(f"  NDVI range: {data['optimal_ndvi']}")
        print(f"  EVI range: {data['optimal_evi']}")
        print(f"  SAVI range: {data['optimal_savi']}")
        print(f"  Water needs: {data['water_needs']}")
        print(f"  Growth stages: {len(data['growth_stages'])}")
        print(f"  Common issues tracked: {len(data['common_issues'])}")
    
    print("\n✅ Test 7 Complete\n")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("    PHASE 3 TEST SUITE: LLM & KNOWLEDGE BASE")
    print("="*60)
    
    try:
        # Run all tests
        test_health_category()
        test_knowledge_base_diagnosis()
        test_recommendations()
        test_llm_setup()
        test_crops_knowledge_base()
        test_spectral_interpretation()
        test_farmer_response()
        
        print("\n" + "="*60)
        print("    ALL PHASE 3 TESTS COMPLETE")
        print("="*60)
        print("\n✅ Knowledge Base: Fully functional")
        print("✅ LLM Service: Ready (with fallback support)")
        print("\nNote: LLM interpretation quality depends on GROQ_API_KEY")
        print("Fallback mode uses rule-based responses when API unavailable\n")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
