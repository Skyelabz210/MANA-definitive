#!/usr/bin/env python3
"""
Test script for MCP delegation servers.
Run this to verify your setup is working correctly.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from delegation_router import DelegationRouter, ModelPreference


def test_codex():
    """Test Codex server."""
    print("\n" + "="*60)
    print("Testing Codex Server (Code Generation)")
    print("="*60)

    router = DelegationRouter()

    spec = "Write a Rust function that adds two integers"
    print(f"\nTask: {spec}")
    print("\nCalling Codex...")

    result = router.generate_code(spec, language="rust", model=ModelPreference.CODEX)

    if result["success"]:
        print("\n✓ SUCCESS")
        print(f"\nResponse:\n{result['response']}")
        if "usage" in result:
            print(f"\nTokens used: {result['usage']}")
    else:
        print(f"\n✗ FAILED: {result['error']}")

    return result["success"]


def test_qwen():
    """Test QWEN server."""
    print("\n" + "="*60)
    print("Testing QWEN Server (Mathematical Reasoning)")
    print("="*60)

    router = DelegationRouter()

    problem = "Explain why the Chinese Remainder Theorem allows parallel computation"
    print(f"\nTask: {problem}")
    print("\nCalling QWEN...")

    result = router.execute_request(
        ModelPreference.QWEN,
        "mathematical_reasoning",
        {"problem": problem}
    )

    if result["success"]:
        print("\n✓ SUCCESS")
        print(f"\nResponse:\n{result['response']}")
        if "usage" in result:
            print(f"\nTokens used: {result['usage']}")
    else:
        print(f"\n✗ FAILED: {result['error']}")

    return result["success"]


def test_gemini():
    """Test Gemini server."""
    print("\n" + "="*60)
    print("Testing Gemini Server (Code Analysis)")
    print("="*60)

    router = DelegationRouter()

    code = """
fn divide(a: i32, b: i32) -> i32 {
    a / b  // Potential division by zero!
}
"""
    print(f"\nCode to analyze:\n{code}")
    print("\nCalling Gemini...")

    result = router.analyze_code(code, analysis_type="bugs", model=ModelPreference.GEMINI)

    if result["success"]:
        print("\n✓ SUCCESS")
        print(f"\nAnalysis:\n{result['response']}")
        if "usage" in result:
            print(f"\nTokens used: {result['usage']}")
    else:
        print(f"\n✗ FAILED: {result['error']}")

    return result["success"]


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("MCP Delegation Server Test Suite")
    print("="*60)

    # Check environment variables
    print("\nChecking environment variables...")
    openai_key = os.getenv("OPENAI_API_KEY")
    qwen_key = os.getenv("QWEN_API_KEY") or os.getenv("TOGETHER_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    print(f"  OPENAI_API_KEY: {'✓ Set' if openai_key else '✗ Not set'}")
    print(f"  QWEN_API_KEY: {'✓ Set' if qwen_key else '✗ Not set'}")
    print(f"  GOOGLE_API_KEY: {'✓ Set' if google_key else '✗ Not set'}")

    if not all([openai_key, qwen_key, google_key]):
        print("\n⚠ Warning: Not all API keys are set!")
        print("Please configure your .env file and load it.")
        print("See README.md for instructions.")
        return 1

    # Run tests
    results = {}

    try:
        results["codex"] = test_codex()
    except Exception as e:
        print(f"\n✗ Codex test failed with exception: {e}")
        results["codex"] = False

    try:
        results["qwen"] = test_qwen()
    except Exception as e:
        print(f"\n✗ QWEN test failed with exception: {e}")
        results["qwen"] = False

    try:
        results["gemini"] = test_gemini()
    except Exception as e:
        print(f"\n✗ Gemini test failed with exception: {e}")
        results["gemini"] = False

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    for server, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {server.capitalize()}: {status}")

    all_passed = all(results.values())
    print("\n" + "="*60)

    if all_passed:
        print("✓ All tests passed! Delegation system is ready.")
        return 0
    else:
        print("✗ Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
