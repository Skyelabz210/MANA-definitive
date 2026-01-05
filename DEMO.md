# NINE65 FHE Demo

Standalone BFV homomorphic encryption demo. Linux x86_64.

## Quick Start

```bash
tar xzf fhe_demo_linux_x86_64.tar.gz
chmod +x target/release/fhe_demo
./target/release/fhe_demo
```

## Usage

```
./fhe_demo [--a <u64>] [--b <u64>] [--config <name>] [--seed <u64> | --os-seed]

Options:
  --a <u64>           First plaintext (default: 17)
  --b <u64>           Second plaintext (default: 25)
  --config <name>     he_standard_128 | standard_128 | high_192 | light (default: he_standard_128)
  --seed <u64>        Deterministic RNG seed (default: 42)
  --os-seed           Use OS entropy for RNG
```

## Example Run

```bash
./target/release/fhe_demo
```

Expected output:
```
NINE65 FHE demo
Note: demo uses deterministic Shadow Entropy unless --os-seed is set.
Parameters: n=2048, q=998244353, t=65537, eta=3
Keygen: 2 ms
Results:
  17 + 25 = 42
  25 - 17 = 8
  -17 = 65520 (mod 65537)
  17 + 10 = 27
  17 * 3 = 51
Status: PASS
```

## What It Does

Full BFV workflow:
1. Key generation (public, secret, evaluation keys)
2. Encrypt two plaintexts
3. Homomorphic add, sub, negate
4. Homomorphic add-plain, mul-plain
5. Decrypt and verify correctness

Exit code 0 = all operations passed.

## Configs

| Name | Ring dim | Security | Speed |
|------|----------|----------|-------|
| he_standard_128 | 2048 | 128-bit | fast (default) |
| standard_128 | 4096 | 128-bit | moderate |
| high_192 | 8192 | 192-bit | slower |
| light | 1024 | 80-bit | fastest (testing only) |

## Verify Checksum

```bash
sha256sum -c SHA256SUMS
```

## Notes

- This is a black-box demo binary; implementation details are not public yet
- Focus is on functional correctness and performance
- Questions/feedback welcome
