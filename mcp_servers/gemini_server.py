#!/usr/bin/env python3
"""
MCP Server for Google Gemini Delegation
Provides headless API calls to Gemini for multimodal reasoning and analysis.
"""

import os
import json
import sys
from typing import Any, Dict, List, Optional
import asyncio

try:
    import google.generativeai as genai
except ImportError:
    print("Error: google-generativeai package not installed. Run: pip install google-generativeai", file=sys.stderr)
    sys.exit(1)


class GeminiMCPServer:
    """MCP Server for Google Gemini delegation."""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY environment variable not set")

        genai.configure(api_key=self.api_key)

        # Select model based on task requirements
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        self.model = genai.GenerativeModel(self.model_name)

    async def generate(self, prompt: str, system_instruction: Optional[str] = None,
                      temperature: float = 0.4, max_output_tokens: int = 8192) -> Dict[str, Any]:
        """
        Generate response using Gemini.

        Args:
            prompt: The user prompt
            system_instruction: Optional system instruction
            temperature: Sampling temperature
            max_output_tokens: Maximum output tokens

        Returns:
            Dictionary with response and metadata
        """
        try:
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
            }

            if system_instruction:
                model = genai.GenerativeModel(
                    self.model_name,
                    system_instruction=system_instruction,
                    generation_config=generation_config
                )
            else:
                model = genai.GenerativeModel(
                    self.model_name,
                    generation_config=generation_config
                )

            response = model.generate_content(prompt)

            return {
                "success": True,
                "response": response.text,
                "model": self.model_name,
                "usage": {
                    "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                    "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": self.model_name
            }

    async def analyze_code(self, code: str, analysis_type: str = "bugs") -> Dict[str, Any]:
        """
        Analyze code for bugs, optimizations, or improvements.

        Args:
            code: The code to analyze
            analysis_type: Type of analysis (bugs, optimizations, security, style)

        Returns:
            Dictionary with analysis
        """
        system_instruction = (
            "You are an expert code analyst. Provide thorough, actionable feedback. "
            "For QMNF/NINE65 code, verify integer-only arithmetic and CLAUDE.md compliance."
        )

        analysis_prompts = {
            "bugs": "Identify bugs, logical errors, and potential runtime issues in this code:",
            "optimizations": "Suggest performance optimizations for this code:",
            "security": "Identify security vulnerabilities in this code:",
            "style": "Review code style and best practices for this code:"
        }

        prompt_prefix = analysis_prompts.get(analysis_type, analysis_prompts["bugs"])
        prompt = f"{prompt_prefix}\n\n```\n{code}\n```"

        return await self.generate(prompt, system_instruction=system_instruction, max_output_tokens=8192)

    async def benchmark_analysis(self, benchmark_data: str) -> Dict[str, Any]:
        """
        Analyze benchmark results and provide insights.

        Args:
            benchmark_data: Benchmark results (text or JSON)

        Returns:
            Dictionary with analysis
        """
        system_instruction = (
            "You are an expert in performance analysis. Analyze benchmark results, "
            "identify bottlenecks, compare against baselines, and suggest improvements."
        )

        prompt = f"Analyze these benchmark results:\n\n{benchmark_data}"
        return await self.generate(prompt, system_instruction=system_instruction, max_output_tokens=8192)

    async def mathematical_proof_review(self, proof: str) -> Dict[str, Any]:
        """
        Review mathematical proofs for correctness.

        Args:
            proof: The mathematical proof

        Returns:
            Dictionary with review
        """
        system_instruction = (
            "You are an expert mathematician. Review proofs rigorously, checking for "
            "logical gaps, incorrect assumptions, and missing steps."
        )

        prompt = f"Review this mathematical proof for correctness:\n\n{proof}"
        return await self.generate(prompt, system_instruction=system_instruction, max_output_tokens=8192)

    async def documentation_generation(self, code: str, doc_type: str = "api") -> Dict[str, Any]:
        """
        Generate documentation for code.

        Args:
            code: The code to document
            doc_type: Type of documentation (api, tutorial, reference)

        Returns:
            Dictionary with documentation
        """
        system_instruction = "You are a technical writer. Generate clear, comprehensive documentation."

        doc_prompts = {
            "api": "Generate API documentation for this code:",
            "tutorial": "Generate a tutorial explaining how to use this code:",
            "reference": "Generate reference documentation for this code:"
        }

        prompt_prefix = doc_prompts.get(doc_type, doc_prompts["api"])
        prompt = f"{prompt_prefix}\n\n```\n{code}\n```"

        return await self.generate(prompt, system_instruction=system_instruction, max_output_tokens=8192)

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
        elif method == "analyze_code":
            return asyncio.run(self.analyze_code(**params))
        elif method == "benchmark_analysis":
            return asyncio.run(self.benchmark_analysis(**params))
        elif method == "mathematical_proof_review":
            return asyncio.run(self.mathematical_proof_review(**params))
        elif method == "documentation_generation":
            return asyncio.run(self.documentation_generation(**params))
        else:
            return {"success": False, "error": f"Unknown method: {method}"}


def main():
    """Main entry point for MCP server."""
    server = GeminiMCPServer()

    print("Gemini MCP Server started", file=sys.stderr)
    print("Available methods: generate, analyze_code, benchmark_analysis, mathematical_proof_review, documentation_generation", file=sys.stderr)

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
