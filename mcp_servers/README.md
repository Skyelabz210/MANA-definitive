# MCP Server Delegation System

Headless API delegation to Codex, QWEN, and Gemini for specialized tasks in the NINE65/MANA project.

## Overview

This system provides Model Context Protocol (MCP) servers that delegate tasks to three specialized AI models:

- **Codex (GPT-4)**: Code generation, bug fixing, quick implementations
- **QWEN**: Mathematical reasoning, formal verification, complex proofs
- **Gemini**: Code analysis, benchmarking insights, documentation generation

## Installation

### 1. Install Python Dependencies

```bash
cd /home/acid/Projects/NINE65/MANA_boosted/mcp_servers
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy the template
cp .env.template .env

# Edit .env and add your API keys
nano .env
```

Required API keys:
- `OPENAI_API_KEY`: From OpenAI (https://platform.openai.com/api-keys)
- `QWEN_API_KEY` or `TOGETHER_API_KEY`: From Together AI (https://api.together.xyz/)
- `GOOGLE_API_KEY`: From Google AI Studio (https://makersuite.google.com/app/apikey)

### 3. Load Environment Variables

```bash
# Add to your ~/.bashrc or ~/.zshrc
export $(grep -v '^#' /home/acid/Projects/NINE65/MANA_boosted/mcp_servers/.env | xargs)

# Or load for current session
source <(grep -v '^#' /home/acid/Projects/NINE65/MANA_boosted/mcp_servers/.env | sed 's/^/export /')
```

## Usage

### Direct MCP Server Calls

Each server accepts JSON requests on stdin and returns JSON responses on stdout.

#### Codex Server

```bash
echo '{"method": "complete_code", "params": {"prompt": "Implement a Fibonacci function in Rust"}}' | \
  python3 codex_server.py
```

**Available methods**:
- `complete_code`: Generate code from prompt
- `explain_code`: Explain what code does
- `fix_bugs`: Fix bugs in provided code

#### QWEN Server

```bash
echo '{"method": "mathematical_reasoning", "params": {"problem": "Prove that sqrt(2) is irrational"}}' | \
  python3 qwen_server.py
```

**Available methods**:
- `generate`: General generation with optional system prompt
- `mathematical_reasoning`: Solve mathematical problems
- `code_generation`: Generate code with QMNF/integer-only awareness
- `formal_verification`: Verify code against specifications

#### Gemini Server

```bash
echo '{"method": "analyze_code", "params": {"code": "fn main() { println!(\"Hello\"); }", "analysis_type": "bugs"}}' | \
  python3 gemini_server.py
```

**Available methods**:
- `generate`: General generation
- `analyze_code`: Analyze code (bugs, optimizations, security, style)
- `benchmark_analysis`: Analyze benchmark results
- `mathematical_proof_review`: Review mathematical proofs
- `documentation_generation`: Generate documentation (api, tutorial, reference)

### Intelligent Delegation Router

The router automatically selects the best model for each task type:

```bash
# Generate code (routes to Codex)
python3 delegation_router.py code_generation --spec "Implement CRT reconstruction" --lang rust

# Analyze code (routes to Gemini)
python3 delegation_router.py code_analysis --code "$(cat src/lib.rs)" --type bugs

# Mathematical reasoning (routes to QWEN)
python3 delegation_router.py mathematical_reasoning --problem "Verify K-elimination correctness"
```

### Python API

```python
from delegation_router import DelegationRouter, TaskType, ModelPreference

router = DelegationRouter()

# Automatic routing based on task type
result = router.generate_code("Implement exact division using fused piggyback", language="rust")
print(result["response"])

# Force specific model
result = router.analyze_code(code_snippet, model=ModelPreference.GEMINI)

# Analyze benchmarks
with open("benchmark_results.txt") as f:
    benchmark_data = f.read()
result = router.analyze_benchmarks(benchmark_data)
print(result["response"])
```

## Task-to-Model Mapping

| Task Type | Default Model | Rationale |
|-----------|--------------|-----------|
| Code Generation | Codex | Fastest, most accurate code synthesis |
| Code Explanation | Gemini | Better at natural language explanations |
| Bug Fixing | Codex | Strong at identifying and fixing bugs |
| Code Analysis | Gemini | Comprehensive analysis capabilities |
| Mathematical Reasoning | QWEN | Specialized for mathematical tasks |
| Formal Verification | QWEN | Strong logical reasoning |
| Benchmark Analysis | Gemini | Excellent at data interpretation |
| Documentation | Gemini | Best at technical writing |
| Proof Review | QWEN | Rigorous mathematical validation |

## Integration with Claude Code

### Option 1: MCP Server Configuration

Add to your `.claude/settings.local.json`:

```json
{
  "mcpServers": {
    "codex-delegation": {
      "command": "python3",
      "args": ["/home/acid/Projects/NINE65/MANA_boosted/mcp_servers/codex_server.py"],
      "description": "Delegate to Codex for code generation"
    },
    "qwen-delegation": {
      "command": "python3",
      "args": ["/home/acid/Projects/NINE65/MANA_boosted/mcp_servers/qwen_server.py"],
      "description": "Delegate to QWEN for mathematical reasoning"
    },
    "gemini-delegation": {
      "command": "python3",
      "args": ["/home/acid/Projects/NINE65/MANA_boosted/mcp_servers/gemini_server.py"],
      "description": "Delegate to Gemini for code analysis"
    }
  }
}
```

### Option 2: Bash Tool Integration

From Claude Code, you can call the delegation router:

```bash
python3 /home/acid/Projects/NINE65/MANA_boosted/mcp_servers/delegation_router.py \
  code_generation --spec "Your specification here"
```

## Examples

### Example 1: Generate QMNF-Compliant Code

```python
from delegation_router import DelegationRouter

router = DelegationRouter()

spec = """
Implement a function that computes the exact value of pi to 1000 decimal places
using the QMNF rational arithmetic system. Must use QMNFRational, no floats.
"""

result = router.generate_code(spec, language="rust")

if result["success"]:
    print(result["response"])
    print(f"\nTokens used: {result['usage']['total_tokens']}")
else:
    print(f"Error: {result['error']}")
```

### Example 2: Verify K-Elimination Proof

```python
proof = """
Theorem: K-Elimination provides O(k) complexity for RNS division.

Proof:
1. Given X = vM + k*M where k < A (anchor modulus)
2. X mod A = (vM + k*M) mod A = k*M mod A
3. Since M coprime to A, we can compute k = (X mod A) * M^(-1) mod A
4. This requires O(1) operations in the anchor
5. Lifting to all channels is O(n) where n is number of channels
6. Total complexity: O(k) compared to O(k²) for traditional MRC

QED
"""

result = router.verify_proof(proof)
print(result["response"])
```

### Example 3: Analyze Benchmark Results

```python
with open("/home/acid/Projects/NINE65/MANA_boosted/nine65_rust_bench_results.txt") as f:
    bench_data = f.read()

result = router.analyze_benchmarks(bench_data)

if result["success"]:
    print("Benchmark Analysis:")
    print(result["response"])
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│           Claude Code (Main Agent)              │
└────────────────┬────────────────────────────────┘
                 │
                 │ Delegates via MCP/Bash
                 ▼
┌─────────────────────────────────────────────────┐
│         Delegation Router (Python)              │
│   - Routes tasks to appropriate model           │
│   - Handles request/response formatting         │
└───────┬─────────────┬─────────────┬─────────────┘
        │             │             │
        ▼             ▼             ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│   Codex   │  │   QWEN    │  │  Gemini   │
│  Server   │  │  Server   │  │  Server   │
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘
      │              │              │
      ▼              ▼              ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│  OpenAI   │  │ Together  │  │  Google   │
│    API    │  │    AI     │  │  AI API   │
└───────────┘  └───────────┘  └───────────┘
```

## Cost Estimates

Approximate costs per 1M tokens (as of January 2026):

- **GPT-4 Turbo**: $10 input / $30 output
- **QWEN 2.5 Coder 32B** (via Together AI): $0.80 input / $0.80 output
- **Gemini 2.0 Flash**: $0.15 input / $0.60 output

The router uses the most cost-effective model for each task type.

## Troubleshooting

### API Key Issues

```bash
# Verify environment variables are set
echo $OPENAI_API_KEY
echo $QWEN_API_KEY
echo $GOOGLE_API_KEY

# Test each server individually
echo '{"method": "generate", "params": {"prompt": "test"}}' | python3 codex_server.py
```

### Server Not Responding

Check stderr output:

```bash
python3 codex_server.py 2>&1 | head
```

### Import Errors

Reinstall dependencies:

```bash
pip install --upgrade -r requirements.txt
```

## Security Notes

- Store API keys in `.env` file (never commit to git)
- The `.env` file is already in `.gitignore`
- Use environment variables for sensitive data
- Consider using API key rotation for production use

## Future Enhancements

- [ ] Add retry logic with exponential backoff
- [ ] Implement caching for repeated requests
- [ ] Add cost tracking and budget limits
- [ ] Support streaming responses
- [ ] Add local model fallback options
- [ ] Implement request queuing for rate limits
- [ ] Add telemetry and logging

## License

Same as parent NINE65/MANA project.
