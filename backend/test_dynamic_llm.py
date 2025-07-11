#!/usr/bin/env python3
"""
Test script for dynamic LLM switching functionality
Tests both OpenRouter and OpenAI API routing based on model names
"""

import os
from agents.orchestrator_agent import get_llm

def test_dynamic_llm_switching():
    """Test the dynamic LLM switching functionality"""
    
    # Set environment variables for testing (use your actual API keys)
    os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY", "your-openrouter-api-key-here")
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
    
    print("🔧 Testing dynamic LLM switching...")
    print(f"OPENROUTER_API_KEY set: {bool(os.getenv('OPENROUTER_API_KEY'))}")
    print(f"OPENAI_API_KEY set: {bool(os.getenv('OPENAI_API_KEY'))}")
    print()
    
    # Test cases
    test_cases = [
        ("google/gemini-2.5-flash", "OpenRouter"),
        ("mistral/mistral-small", "OpenRouter"),
        ("gpt-3.5-turbo", "OpenAI"),
        ("gpt-4", "OpenAI"),
        ("claude-3-haiku", "OpenAI"),  # Should fallback to OpenAI for non-google/mistral
    ]
    
    results = []
    
    for model_name, expected_provider in test_cases:
        print(f"Testing model: {model_name} (expecting {expected_provider})")
        try:
            # Test with minimal parameters to avoid compatibility issues
            llm = get_llm(model_name, temperature=0.3, max_tokens=1500)
            llm_type = getattr(llm, '_llm_type', 'unknown')
            provider = "OpenRouter" if llm_type == "openrouter" else "OpenAI" if llm_type in ["openai-llm", "openai-chat"] else "Unknown"
            
            print(f"  ✅ LLM created: {type(llm).__name__} - {llm_type}")
            print(f"  📍 Provider: {provider}")
            
            if provider == expected_provider:
                print(f"  🎯 Routing correct!")
                results.append(True)
            else:
                print(f"  ⚠️ Expected {expected_provider}, got {provider}")
                results.append(False)
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append(False)
        
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All dynamic LLM switching tests passed!")
    else:
        print(f"⚠️ {total - passed} tests failed")
    
    return passed == total

def test_simple_llm_call():
    """Test a simple LLM call to verify it works"""
    print("\n🧪 Testing simple LLM call...")
    
    try:
        # Test with a google model (should route to OpenRouter)
        llm = get_llm("google/gemini-2.5-flash")
        response = llm._call("What is 2 + 2?")
        print(f"✅ OpenRouter response: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting LLM integration tests...\n")
    
    routing_test = test_dynamic_llm_switching()
    call_test = test_simple_llm_call()
    
    print(f"\n📊 Final Results:")
    print(f"  Dynamic routing: {'✅ PASS' if routing_test else '❌ FAIL'}")
    print(f"  Simple LLM call: {'✅ PASS' if call_test else '❌ FAIL'}")
    
    if routing_test and call_test:
        print("\n🎉 All tests passed! The LLM integration is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.") 