#!/usr/bin/env python3
"""
Example: Analyze NINE65 benchmark results using Gemini delegation.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from delegation_router import DelegationRouter


def main():
    """Analyze benchmark results from NINE65."""
    router = DelegationRouter()

    # Read benchmark results
    benchmark_file = "/home/acid/Projects/NINE65/MANA_boosted/nine65_rust_bench_results.txt"

    if not os.path.exists(benchmark_file):
        print(f"Error: Benchmark file not found at {benchmark_file}")
        return 1

    with open(benchmark_file, "r") as f:
        benchmark_data = f.read()

    print("Analyzing NINE65 benchmark results using Gemini...")
    print(f"File: {benchmark_file}")
    print(f"Size: {len(benchmark_data)} bytes")
    print("\nSending to Gemini for analysis...\n")

    result = router.analyze_benchmarks(benchmark_data)

    if result["success"]:
        print("="*60)
        print("BENCHMARK ANALYSIS")
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
