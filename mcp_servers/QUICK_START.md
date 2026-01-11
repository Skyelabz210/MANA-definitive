# MCP Delegation Quick Start Guide

Get up and running with Codex, QWEN, and Gemini delegation in 5 minutes.

## Step 1: Install Dependencies (1 minute)

```bash
cd /home/acid/Projects/NINE65/MANA_boosted/mcp_servers
pip install -r requirements.txt
```

## Step 2: Configure API Keys (2 minutes)

```bash
# Copy template
cp .env.template .env

# Edit with your API keys
nano .env
```

Get your API keys:
- **OpenAI**: https://platform.openai.com/api-keys
- **Together AI** (for QWEN): https://api.together.xyz/
- **Google AI**: https://makersuite.google.com/app/apikey

## Step 3: Load Environment (30 seconds)

```bash
# Add to your shell profile (~/.bashrc or ~/.zshrc)
export $(grep -v '^#' /home/acid/Projects/NINE65/MANA_boosted/mcp_servers/.env | xargs)

# Or for this session only
source <(grep -v '^#' /home/acid/Projects/NINE65/MANA_boosted/mcp_servers/.env | sed 's/^/export /')
```

## Step 4: Test Setup (1 minute)

```bash
cd /home/acid/Projects/NINE65/MANA_boosted/mcp_servers
python3 examples/test_delegation.py
```

You should see:
```
✓ All tests passed! Delegation system is ready.
```

## Step 5: Use It! (30 seconds)

### From Python:

```python
from delegation_router import DelegationRouter

router = DelegationRouter()

# Generate code
result = router.generate_code("Implement Fibonacci in Rust")
print(result["response"])

# Analyze benchmarks
with open("benchmark_results.txt") as f:
    result = router.analyze_benchmarks(f.read())
print(result["response"])
```

### From Command Line:

```bash
# Generate code
python3 delegation_router.py code_generation \
  --spec "Implement exact division using QMNFRational" \
  --lang rust

# Analyze code
python3 delegation_router.py code_analysis \
  --code "$(cat src/lib.rs)" \
  --type bugs
```

### From Claude Code:

Just call it from bash:

```bash
python3 /home/acid/Projects/NINE65/MANA_boosted/mcp_servers/delegation_router.py \
  code_generation --spec "Your task here"
```

## Common Use Cases

### 1. Generate QMNF-Compliant Code

```bash
python3 examples/code_generation_example.py
```

### 2. Analyze Benchmark Results

```bash
python3 examples/benchmark_analysis_example.py
```

### 3. Verify Mathematical Proofs

```bash
python3 examples/proof_verification_example.py
```

## Troubleshooting

**Problem**: "API key not set"
**Solution**: Make sure you've loaded the .env file (Step 3)

**Problem**: "Module not found"
**Solution**: Run `pip install -r requirements.txt` again

**Problem**: "Request timeout"
**Solution**: Check your internet connection and API key validity

## Cost Optimization

The router automatically selects cost-effective models:

- Quick code tasks → Codex (GPT-4)
- Math/proofs → QWEN via Together AI ($0.80/M tokens)
- Analysis/docs → Gemini Flash ($0.15-$0.60/M tokens)

Estimated cost for typical session: $0.10 - $1.00

## Next Steps

Read the full documentation:
- [README.md](README.md) - Complete guide
- [mcp_config.json](mcp_config.json) - Claude Code integration
- [examples/](examples/) - More examples

## Support

Issues? Check:
1. Environment variables are set correctly
2. API keys are valid and have credits
3. Python dependencies are installed
4. Internet connection is working

Still stuck? Check the error messages - they're designed to be helpful!
