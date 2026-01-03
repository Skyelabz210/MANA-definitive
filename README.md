# MANA FHE - Private Development Repository

**Status**: PRIVATE - Internal Development Only
**Owner**: HackFate.us Research

---

## Overview

This repository contains ongoing private development work for MANA FHE (Modular Arithmetic for Neural Applications - Fully Homomorphic Encryption).

This is separate from the public K-Elimination release.

## Contents

### Security Proofs (`/src/`)

Self-cryptanalysis toolkit for validating MANA FHE security:

- `main.rs` - Attack cost estimator (Primal, Dual, Hybrid, HE Standard)
- `k_elimination_attack.rs` - K-Elimination specific attack analysis
- `lattice_attack.rs` - LLL/BKZ lattice attack simulations

### Documentation

- `SECURITY_ANALYSIS_REPORT.md` - Full security analysis report

## Building

```bash
cargo build --release

# Run attack estimator
./target/release/attack-estimator

# Run K-Elimination attack analysis
./target/release/k-elimination-attack

# Run lattice attack simulation
./target/release/lattice-attack
```

## Key Findings

| Attack | Status |
|--------|--------|
| Shor's Algorithm | DOES NOT APPLY (Ring-LWE) |
| Primal/Dual Lattice | 96-256 bit security |
| K-Elimination Inversion | Infeasible (2^60 uncertainty) |
| RNS Correlation | No leakage (CRT secure) |
| Timing Side-Channel | Constant-time |

## License

PROPRIETARY - All Rights Reserved
HackFate.us Research

NOT FOR PUBLIC DISTRIBUTION
