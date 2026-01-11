---
description: Smart local model delegation with automatic model selection
---

Analyze the task and automatically select the best local model:

**Task analysis for**: "{{prompt}}"

**If code generation** (keywords: implement, write code, function, class):
```bash
cd /home/acid/Projects/NINE65/MANA_boosted/mcp_servers && \
python3 chunked_model_inference.py \
  "deepseek-coder-6.7b-instruct.Q4_K_M" \
  "{{prompt}}"
```

**If mathematical reasoning** (keywords: prove, calculate, solve, theorem):
```bash
cd /home/acid/Projects/NINE65/MANA_boosted/mcp_servers && \
python3 chunked_model_inference.py \
  "wizardmath-7b-v1.1-Q4_K_M" \
  "Solve step-by-step: {{prompt}}"
```

**If complex Python** (keywords: complex, large, sophisticated Python code):
```bash
cd /home/acid/Projects/NINE65/MANA_boosted/mcp_servers && \
python3 chunked_model_inference.py \
  "wizardcoder-python-13b-Q4_K_M" \
  "{{prompt}}"
```

Choose the most appropriate model based on the task complexity and type.
