#!/usr/bin/env python3
"""
Example: Generate QMNF-compliant code using Codex/QWEN delegation.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from delegation_router import DelegationRouter, ModelPreference


def main():
    """Generate QMNF-compliant code."""
    router = DelegationRouter()

    specification = """
Implement a Rust function that computes the exact greatest common divisor (GCD)
of two QMNFRational numbers using the Euclidean algorithm.

Requirements:
- Use the QMNFRational type from the QMNF system
- Must be integer-only (no floating-point operations)
- Include proper error handling
- Add documentation comments
- Follow Rust best practices

The function signature should be:
pub fn rational_gcd(a: QMNFRational, b: QMNFRational) -> Result<QMNFRational, Nine65Error>
"""

    print("Generating QMNF-compliant GCD implementation...")
    print(f"\nSpecification:\n{specification}")
    print("\n" + "="*60)
    print("Delegating to Codex (GPT-4)...")
    print("="*60 + "\n")

    result = router.generate_code(specification, language="rust", model=ModelPreference.CODEX)

    if result["success"]:
        print("Generated Code:")
        print("="*60)
        print(result["response"])
        print("="*60)

        if "usage" in result:
            print(f"\nTokens used: {result['usage']}")

        # Optionally save to file
        output_file = "/tmp/generated_rational_gcd.rs"
        with open(output_file, "w") as f:
            f.write(result["response"])
        print(f"\nCode saved to: {output_file}")

        return 0
    else:
        print(f"Error: {result['error']}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
