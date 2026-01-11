#!/usr/bin/env python3
"""
Example: Verify mathematical proofs using QWEN delegation.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from delegation_router import DelegationRouter, ModelPreference


def main():
    """Verify K-Elimination proof."""
    router = DelegationRouter()

    proof = """
Theorem: The K-Elimination innovation provides O(k) complexity for RNS division,
where k is the number of anchor channels, compared to O(k²) for traditional
Multi-Residue Conversion (MRC).

Proof:

Given:
- X is an integer represented in RNS across n computational channels
- M is a product of n coprime moduli: M = m₁ × m₂ × ... × mₙ
- A is an anchor modulus coprime to M
- We want to compute X/M

Traditional MRC approach:
1. Reconstruct X from all n residues: O(n²) using CRT
2. Perform division: O(1)
3. Convert back to RNS: O(n²)
Total: O(n²)

K-Elimination approach:
1. Observe that X = vM + k*M where k < A (by construction)
2. In the anchor channel: X mod A = (vM + k*M) mod A = k*M mod A
3. Since M and A are coprime, M has an inverse modulo A
4. Compute k = (X mod A) × M⁻¹ mod A  [O(1) operation]
5. Verify k is correct by checking in a second anchor [O(1)]
6. Use affine lifting to propagate k to all n channels [O(n)]
Total: O(k) = O(1) for anchors + O(n) for lifting

The key insight is that we avoid full CRT reconstruction by working
in the anchor space first, where the division information is directly
available due to the coprimality of M and A.

Correctness:
- X mod A uniquely determines k since k < A
- Coprimality ensures M⁻¹ mod A exists
- Affine lifting preserves correctness across all channels
- Piggyback lifting bounds error by GCD of lifted values

QED

This represents a 40× speedup in practice for systems with 64+ computational
channels and 2-3 anchor channels.
"""

    print("Verifying K-Elimination proof using QWEN...")
    print("\n" + "="*60)
    print("PROOF TO VERIFY")
    print("="*60)
    print(proof)
    print("\n" + "="*60)
    print("Delegating to QWEN for verification...")
    print("="*60 + "\n")

    result = router.verify_proof(proof, model=ModelPreference.QWEN)

    if result["success"]:
        print("="*60)
        print("VERIFICATION RESULT")
        print("="*60)
        print(result["response"])
        print("\n" + "="*60)

        if "usage" in result:
            print(f"\nTokens used: {result['usage']}")

        return 0
    else:
        print(f"Error: {result['error']}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
