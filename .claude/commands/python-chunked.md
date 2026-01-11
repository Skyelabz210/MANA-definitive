---
description: Run WizardCoder Python 13B with tensor chunking (powerful but slow)
---

Execute Python code generation using the large 13B model:

```bash
cd /home/acid/Projects/NINE65/MANA_boosted/mcp_servers && \
python3 chunked_model_inference.py \
  "wizardcoder-python-13b-Q4_K_M" \
  "{{prompt}}" \
  --max-tokens 2500
```

⚠️ **Note**: This is a 7.5GB model that technically shouldn't run on this system.
Thanks to tensor chunking, it works but is slower (~30-60 seconds per request).

Use for:
- Complex Python implementations
- When quality > speed
- Large codebases generation
