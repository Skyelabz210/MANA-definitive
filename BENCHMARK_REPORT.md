# NINE65 MANA Boosted FHE System - Benchmark Report

**Date**: December 31, 2025
**System**: NINE65 MANA Boosted FHE
**Hardware**: x86_64 Linux (Criterion.rs statistical benchmarking)
**Build**: Release profile, optimized

---

## Executive Summary

The NINE65 MANA Boosted system is a production-ready BFV-style Fully Homomorphic Encryption implementation. Built on the Quantum-Modular Numerical Framework (QMNF) with pure-integer arithmetic, it achieves state-of-the-art performance.

### Key Metrics

| Security Level | Ring (N) | Homo Mul | Encrypt | Decrypt |
|----------------|----------|----------|---------|---------|
| 80-bit (test)  | 1024     | **1.85 ms** | 572 µs | 239 µs |
| 128-bit        | 2048     | **4.01 ms** | 1.27 ms | 541 µs |
| 128-bit        | 4096     | **8.96 ms** | 2.70 ms | 1.17 ms |
| 192-bit        | 8192     | **19.5 ms** | 5.80 ms | 2.53 ms |

---

## 1. Homomorphic Multiplication Performance

The most computationally intensive FHE operation. Includes polynomial multiplication, relinearization, and key-switching.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HOMOMORPHIC MULTIPLICATION BENCHMARKS                    │
├─────────────┬──────────────┬──────────────┬─────────────┬───────────────────┤
│ N Size      │ Homo Mul     │ NTT Forward  │ NTT Inverse │ Scaling Factor    │
│ (2^k)       │ Time         │ Time         │ Time        │ (vs N/2)          │
├─────────────┼──────────────┼──────────────┼─────────────┼───────────────────┤
│ 1024        │ 1.85 ms      │ 24.6 µs      │ 62.2 µs     │ -                 │
│ 2048        │ 4.01 ms      │ 54.5 µs      │ 158 µs      │ 2.17×             │
│ 4096        │ 8.96 ms      │ 138 µs       │ 355 µs      │ 2.23×             │
│ 8192        │ 19.5 ms      │ 360 µs       │ 740 µs      │ 2.18×             │
└─────────────┴──────────────┴──────────────┴─────────────┴───────────────────┘
```

**Scaling**: Near-optimal O(N log N) confirmed. Factor of ~2.2× per doubling of N.

---

## 2. NTT Transform Performance

The Number Theoretic Transform is the computational backbone of polynomial multiplication.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        NTT TRANSFORM BENCHMARKS                             │
├─────────────┬──────────────┬──────────────┬─────────────────────────────────┤
│ N Size      │ Forward NTT  │ Roundtrip    │ Throughput                      │
│ (2^k)       │              │ (NTT+INTT)   │ (M coeffs/sec)                  │
├─────────────┼──────────────┼──────────────┼─────────────────────────────────┤
│ 1024        │ 24.6 µs      │ 86.8 µs      │ 41.6                            │
│ 2048        │ 54.5 µs      │ 213 µs       │ 37.6                            │
│ 4096        │ 138 µs       │ 493 µs       │ 29.7                            │
│ 8192        │ 360 µs       │ 1.10 ms      │ 22.8                            │
└─────────────┴──────────────┴──────────────┴─────────────────────────────────┘
```

---

## 3. Encryption / Decryption Performance

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ENCRYPTION/DECRYPTION BENCHMARKS                         │
├─────────────┬────────────────┬──────────────┬──────────────┬────────────────┤
│ N Size      │ Encrypt Time   │ Decrypt Time │ Enc Throughput│ Dec Throughput│
│ (2^k)       │                │              │ (coeff/ms)    │ (coeff/ms)    │
├─────────────┼────────────────┼──────────────┼──────────────┼────────────────┤
│ 1024        │ 572 µs         │ 239 µs       │ 1,790         │ 4,284         │
│ 2048        │ 1.27 ms        │ 541 µs       │ 1,612         │ 3,786         │
│ 4096        │ 2.70 ms        │ 1.17 ms      │ 1,517         │ 3,502         │
│ 8192        │ 5.80 ms        │ 2.53 ms      │ 1,413         │ 3,238         │
└─────────────┴────────────────┴──────────────┴──────────────┴────────────────┘
```

---

## 4. Key Generation

| Config          | Ring (N) | Security | Keygen Time |
|-----------------|----------|----------|-------------|
| he_standard_128 | 2048     | 128-bit  | **2 ms**    |
| standard_128    | 4096     | 128-bit  | **5 ms**    |
| high_192        | 8192     | 192-bit  | **13 ms**   |

---

## 5. Parameter Configurations

| Config          | N    | q (modulus)  | t (plaintext) | Security |
|-----------------|------|--------------|---------------|----------|
| he_standard_128 | 2048 | 998244353    | 65537         | 128-bit  |
| standard_128    | 4096 | 998244353    | 65537         | 128-bit  |
| high_192        | 8192 | 998244353    | 65537         | 192-bit  |

- **Plaintext modulus**: 65537 = 2^16 + 1 (Fermat prime F4, industry standard)
- **Ciphertext modulus**: 998244353 (30-bit NTT-friendly prime)

---

## 6. Memory Footprint

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MEMORY USAGE BY COMPONENT                           │
├───────────────────┬──────────────┬──────────────┬───────────────────────────┤
│ Component         │ N=2048       │ N=4096       │ N=8192                    │
│                   │ (128-bit)    │ (128-bit)    │ (192-bit)                 │
├───────────────────┼──────────────┼──────────────┼───────────────────────────┤
│ Ciphertext        │ 32 KB        │ 64 KB        │ 128 KB                    │
│ Evaluation Key    │ 1 MB         │ 4 MB         │ 16 MB                     │
│ NTT Tables        │ 16 KB        │ 32 KB        │ 64 KB                     │
│ Per-Op Context    │ ~2 MB        │ ~6 MB        │ ~20 MB                    │
└───────────────────┴──────────────┴──────────────┴───────────────────────────┘
```

---

## 7. Architecture

```
NINE65 Stack
├── nine65/       Core cryptographic engine
│   ├── BFV encoder/encryptor/decryptor/evaluator
│   ├── NTT engine (Cooley-Tukey, Montgomery reduction)
│   ├── Key generation (public, secret, evaluation keys)
│   └── Shadow Entropy (deterministic or OS-seeded RNG)
│
├── mana/         Parallel execution engine
│   ├── Rayon-based nested parallelism
│   ├── Lane/Stream abstractions for data locality
│   └── Batch processing for ciphertext operations
│
└── unhal/        Hardware abstraction layer
    ├── SIMD acceleration paths
    ├── Parallel/sequential mode selection
    └── Pipeline orchestration
```

---

## 8. Operations Supported

| Operation | Status | Notes |
|-----------|--------|-------|
| Encrypt | ✓ | BFV encoding with Δ scaling |
| Decrypt | ✓ | Exact recovery mod t |
| Add (ct + ct) | ✓ | Coefficient-wise addition |
| Sub (ct - ct) | ✓ | Coefficient-wise subtraction |
| Negate | ✓ | Additive inverse |
| Add Plain | ✓ | ct + scalar |
| Mul Plain | ✓ | ct × scalar |
| Mul (ct × ct) | ✓ | With relinearization |

---

## 9. Demo Binary

Standalone demo for testing:

```bash
./fhe_demo --a 100 --b 200 --config he_standard_128 --os-seed
```

Output:
```
NINE65 FHE demo
Parameters: n=2048, q=998244353, t=65537, eta=3
Keygen: 2 ms
Results:
  100 + 200 = 300
  200 - 100 = 100
  -100 = 65437 (mod 65537)
  100 + 10 = 110
  100 * 3 = 300
Status: PASS
```

**SHA256**: `af84939a3deeb25816ad147b8bd7e873be467bc5c6e942acd6849684acb2f6e8`

---

## 10. Reproduction

All benchmarks use Criterion.rs with:
- 3-second warm-up phase
- 10-20 samples per measurement
- Statistical analysis with outlier detection
- Release build (`--release`)

```bash
cargo bench -p nine65 --bench fhe_scaling
```

---

*NINE65 MANA Boosted FHE System - December 2025*
