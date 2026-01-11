#!/usr/bin/env python3
"""
MCP Server for OpenAI Codex Delegation
Provides headless API calls to OpenAI Codex for code generation tasks.
"""

import os
import json
import sys
from typing import Any, Dict, List, Optional
import asyncio
import anthropic
from anthropic import Anthropic

# For OpenAI Codex, we'll use the OpenAI API client
try:
    import openai
except ImportError:
    print("Error: openai package not installed. Run: pip install openai", file=sys.stderr)
    sys.exit(1)


class CodexMCPServer:
    """MCP Server for OpenAI Codex delegation."""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        openai.api_key = self.api_key
        self.model = os.getenv("OPENAI_CODEX_MODEL", "gpt-4")  # Codex models are deprecated, using GPT-4

    async def complete_code(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.2) -> Dict[str, Any]:
        """
        Generate code completion using Codex/GPT-4.

        Args:
            prompt: The code prompt or context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)

        Returns:
            Dictionary with completion and metadata
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert programmer. Generate clean, efficient code following best practices."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )

            return {
                "success": True,
                "completion": response.choices[0].message.content,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": self.model
            }

    async def explain_code(self, code: str) -> Dict[str, Any]:
        """
        Explain what a code snippet does.

        Args:
            code: The code to explain

        Returns:
            Dictionary with explanation
        """
        prompt = f"Explain what this code does:\n\n```\n{code}\n```"
        return await self.complete_code(prompt, max_tokens=1000)

    async def fix_bugs(self, code: str, error: Optional[str] = None) -> Dict[str, Any]:
        """
        Fix bugs in code.

        Args:
            code: The buggy code
            error: Optional error message

        Returns:
            Dictionary with fixed code
        """
        prompt = f"Fix the bugs in this code:\n\n```\n{code}\n```"
        if error:
            prompt += f"\n\nError message:\n{error}"

        return await self.complete_code(prompt, max_tokens=2000)

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP requests.

        Args:
            request: MCP request dictionary

        Returns:
            MCP response dictionary
        """
        method = request.get("method")
        params = request.get("params", {})

        if method == "complete_code":
            return asyncio.run(self.complete_code(**params))
        elif method == "explain_code":
            return asyncio.run(self.explain_code(**params))
        elif method == "fix_bugs":
            return asyncio.run(self.fix_bugs(**params))
        else:
            return {"success": False, "error": f"Unknown method: {method}"}


def main():
    """Main entry point for MCP server."""
    server = CodexMCPServer()

    print("Codex MCP Server started", file=sys.stderr)
    print("Available methods: complete_code, explain_code, fix_bugs", file=sys.stderr)

    # Read requests from stdin (MCP protocol)
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except Exception as e:
            error_response = {"success": False, "error": str(e)}
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
