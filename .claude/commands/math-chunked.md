---
description: Run WizardMath locally with tensor chunking for mathematical reasoning
---

Execute mathematical reasoning using chunked inference:

```bash
cd /home/acid/Projects/NINE65/MANA_boosted/mcp_servers && \
python3 chunked_model_inference.py \
  "wizardmath-7b-v1.1-Q4_K_M" \
  "Solve this step-by-step: {{prompt}}" \
  --max-tokens 3000
```

This command:
- Uses WizardMath 7B (specialized for mathematical reasoning)
- Runs locally with tensor chunking
- Provides step-by-step solutions
- No API keys needed
