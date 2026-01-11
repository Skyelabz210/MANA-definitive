---
description: Run DeepSeek Coder locally with tensor chunking (no API key needed)
---

Execute code generation using chunked inference:

```bash
cd /home/acid/Projects/NINE65/MANA_boosted/mcp_servers && \
python3 chunked_model_inference.py \
  "deepseek-coder-6.7b-instruct.Q4_K_M" \
  "{{prompt}}"
```

This command:
- Runs locally (no API keys)
- Uses TensorChunkCache to handle the 3.9GB model
- Memory-efficient (only loads needed chunks)
- Outputs code directly to the conversation
