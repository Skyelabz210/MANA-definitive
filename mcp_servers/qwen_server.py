#!/usr/bin/env python3
"""
MCP Server for QWEN (Alibaba) Delegation
Provides headless API calls to QWEN for mathematical reasoning and code tasks.
"""

import os
import json
import sys
from typing import Any, Dict, List, Optional
import asyncio

# QWEN can be accessed via Hugging Face or direct API
try:
    import requests
except ImportError:
    print("Error: requests package not installed. Run: pip install requests", file=sys.stderr)
    sys.exit(1)


class QwenMCPServer:
    """MCP Server for QWEN delegation."""

    def __init__(self):
        # QWEN can be accessed via multiple endpoints
        self.api_endpoint = os.getenv("QWEN_API_ENDPOINT", "https://api.together.xyz/v1/chat/completions")
        self.api_key = os.getenv("QWEN_API_KEY") or os.getenv("TOGETHER_API_KEY")

        if not self.api_key:
            raise ValueError("QWEN_API_KEY or TOGETHER_API_KEY environment variable not set")

        self.model = os.getenv("QWEN_MODEL", "Qwen/Qwen2.5-Coder-32B-Instruct")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def generate(self, prompt: str, system_prompt: Optional[str] = None,
                      max_tokens: int = 4000, temperature: float = 0.3) -> Dict[str, Any]:
        """
        Generate response using QWEN.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Dictionary with response and metadata
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }

            response = requests.post(
                self.api_endpoint,
                headers=self.headers,
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response": data["choices"][0]["message"]["content"],
                    "model": self.model,
                    "usage": data.get("usage", {})
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code} - {response.text}",
                    "model": self.model
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": self.model
            }

    async def mathematical_reasoning(self, problem: str) -> Dict[str, Any]:
        """
        Solve mathematical problems using QWEN.

        Args:
            problem: Mathematical problem description

        Returns:
            Dictionary with solution
        """
        system_prompt = (
            "You are an expert mathematician. Solve problems step-by-step with clear reasoning. "
            "For QMNF system problems, use exact arithmetic (rationals) and avoid floating-point."
        )
        return await self.generate(problem, system_prompt=system_prompt, max_tokens=4000)

    async def code_generation(self, specification: str, language: str = "rust") -> Dict[str, Any]:
        """
        Generate code from specification.

        Args:
            specification: Code specification
            language: Programming language

        Returns:
            Dictionary with generated code
        """
        system_prompt = (
            f"You are an expert {language} programmer. Generate clean, efficient, well-documented code. "
            "For QMNF/NINE65 projects, use integer-only arithmetic and follow the CLAUDE.md guidelines."
        )
        prompt = f"Generate {language} code for:\n\n{specification}"
        return await self.generate(prompt, system_prompt=system_prompt, max_tokens=4000)

    async def formal_verification(self, code: str, specification: str) -> Dict[str, Any]:
        """
        Verify code against formal specification.

        Args:
            code: The code to verify
            specification: Formal specification

        Returns:
            Dictionary with verification results
        """
        system_prompt = "You are an expert in formal verification. Analyze code correctness rigorously."
        prompt = f"Verify this code against the specification:\n\nCode:\n```\n{code}\n```\n\nSpecification:\n{specification}"
        return await self.generate(prompt, system_prompt=system_prompt, max_tokens=4000)

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

        if method == "generate":
            return asyncio.run(self.generate(**params))
        elif method == "mathematical_reasoning":
            return asyncio.run(self.mathematical_reasoning(**params))
        elif method == "code_generation":
            return asyncio.run(self.code_generation(**params))
        elif method == "formal_verification":
            return asyncio.run(self.formal_verification(**params))
        else:
            return {"success": False, "error": f"Unknown method: {method}"}


def main():
    """Main entry point for MCP server."""
    server = QwenMCPServer()

    print("QWEN MCP Server started", file=sys.stderr)
    print("Available methods: generate, mathematical_reasoning, code_generation, formal_verification", file=sys.stderr)

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
