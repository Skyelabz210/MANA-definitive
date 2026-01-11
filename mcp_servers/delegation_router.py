#!/usr/bin/env python3
"""
Intelligent Delegation Router for MCP Servers
Routes tasks to the most appropriate model based on task type and requirements.
"""

import json
import subprocess
import sys
from typing import Any, Dict, Optional, Literal
from enum import Enum


class TaskType(Enum):
    """Types of tasks that can be delegated."""
    CODE_GENERATION = "code_generation"
    CODE_EXPLANATION = "code_explanation"
    BUG_FIXING = "bug_fixing"
    CODE_ANALYSIS = "code_analysis"
    MATHEMATICAL_REASONING = "mathematical_reasoning"
    FORMAL_VERIFICATION = "formal_verification"
    BENCHMARK_ANALYSIS = "benchmark_analysis"
    DOCUMENTATION = "documentation"
    PROOF_REVIEW = "proof_review"


class ModelPreference(Enum):
    """Model preferences based on task characteristics."""
    CODEX = "codex"     # Best for code generation and quick fixes
    QWEN = "qwen"       # Best for mathematical reasoning and verification
    GEMINI = "gemini"   # Best for analysis, documentation, and multimodal tasks


class DelegationRouter:
    """Routes tasks to appropriate MCP servers."""

    # Task to model mapping based on strengths
    TASK_MODEL_MAP = {
        TaskType.CODE_GENERATION: ModelPreference.CODEX,
        TaskType.CODE_EXPLANATION: ModelPreference.GEMINI,
        TaskType.BUG_FIXING: ModelPreference.CODEX,
        TaskType.CODE_ANALYSIS: ModelPreference.GEMINI,
        TaskType.MATHEMATICAL_REASONING: ModelPreference.QWEN,
        TaskType.FORMAL_VERIFICATION: ModelPreference.QWEN,
        TaskType.BENCHMARK_ANALYSIS: ModelPreference.GEMINI,
        TaskType.DOCUMENTATION: ModelPreference.GEMINI,
        TaskType.PROOF_REVIEW: ModelPreference.QWEN,
    }

    SERVER_PATHS = {
        ModelPreference.CODEX: "/home/acid/Projects/NINE65/MANA_boosted/mcp_servers/codex_server.py",
        ModelPreference.QWEN: "/home/acid/Projects/NINE65/MANA_boosted/mcp_servers/qwen_server.py",
        ModelPreference.GEMINI: "/home/acid/Projects/NINE65/MANA_boosted/mcp_servers/gemini_server.py",
    }

    def __init__(self):
        """Initialize the delegation router."""
        pass

    def route_task(self, task_type: TaskType, override_model: Optional[ModelPreference] = None) -> ModelPreference:
        """
        Route a task to the appropriate model.

        Args:
            task_type: The type of task
            override_model: Optional model to force usage

        Returns:
            The selected model preference
        """
        if override_model:
            return override_model

        return self.TASK_MODEL_MAP.get(task_type, ModelPreference.GEMINI)

    def execute_request(self, model: ModelPreference, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a request on the specified MCP server.

        Args:
            model: The model to use
            method: The method to call
            params: Parameters for the method

        Returns:
            Response from the MCP server
        """
        server_path = self.SERVER_PATHS[model]

        request = {
            "method": method,
            "params": params
        }

        try:
            # Start the MCP server process
            process = subprocess.Popen(
                ["python3", server_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Send request
            request_json = json.dumps(request) + "\n"
            stdout, stderr = process.communicate(input=request_json, timeout=300)

            # Parse response
            if stdout.strip():
                response = json.loads(stdout.strip())
                return response
            else:
                return {
                    "success": False,
                    "error": f"No response from server. Stderr: {stderr}"
                }

        except subprocess.TimeoutExpired:
            process.kill()
            return {
                "success": False,
                "error": "Request timed out after 5 minutes"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}"
            }

    # Convenience methods for common tasks

    def generate_code(self, specification: str, language: str = "rust",
                     model: Optional[ModelPreference] = None) -> Dict[str, Any]:
        """Generate code from specification."""
        selected_model = model or self.route_task(TaskType.CODE_GENERATION)

        if selected_model == ModelPreference.CODEX:
            prompt = f"Generate {language} code:\n\n{specification}"
            return self.execute_request(selected_model, "complete_code", {"prompt": prompt})
        elif selected_model == ModelPreference.QWEN:
            return self.execute_request(selected_model, "code_generation",
                                       {"specification": specification, "language": language})
        else:
            return {"success": False, "error": f"Model {selected_model} doesn't support code generation"}

    def analyze_code(self, code: str, analysis_type: str = "bugs",
                    model: Optional[ModelPreference] = None) -> Dict[str, Any]:
        """Analyze code for issues."""
        selected_model = model or self.route_task(TaskType.CODE_ANALYSIS)

        return self.execute_request(selected_model, "analyze_code",
                                    {"code": code, "analysis_type": analysis_type})

    def verify_proof(self, proof: str, model: Optional[ModelPreference] = None) -> Dict[str, Any]:
        """Verify mathematical proof."""
        selected_model = model or self.route_task(TaskType.PROOF_REVIEW)

        if selected_model == ModelPreference.QWEN:
            return self.execute_request(selected_model, "mathematical_reasoning", {"problem": proof})
        elif selected_model == ModelPreference.GEMINI:
            return self.execute_request(selected_model, "mathematical_proof_review", {"proof": proof})
        else:
            return {"success": False, "error": f"Model {selected_model} doesn't support proof verification"}

    def analyze_benchmarks(self, benchmark_data: str,
                          model: Optional[ModelPreference] = None) -> Dict[str, Any]:
        """Analyze benchmark results."""
        selected_model = model or self.route_task(TaskType.BENCHMARK_ANALYSIS)

        return self.execute_request(selected_model, "benchmark_analysis",
                                    {"benchmark_data": benchmark_data})

    def generate_documentation(self, code: str, doc_type: str = "api",
                              model: Optional[ModelPreference] = None) -> Dict[str, Any]:
        """Generate documentation."""
        selected_model = model or self.route_task(TaskType.DOCUMENTATION)

        return self.execute_request(selected_model, "documentation_generation",
                                    {"code": code, "doc_type": doc_type})


def main():
    """CLI interface for delegation router."""
    if len(sys.argv) < 2:
        print("Usage: delegation_router.py <task_type> [options]")
        print("\nTask types:")
        for task in TaskType:
            print(f"  - {task.value}")
        print("\nExamples:")
        print("  delegation_router.py code_generation --spec 'function to add two numbers' --lang rust")
        print("  delegation_router.py code_analysis --code 'fn main() { }' --type bugs")
        sys.exit(1)

    router = DelegationRouter()
    task_type_str = sys.argv[1]

    try:
        task_type = TaskType(task_type_str)
    except ValueError:
        print(f"Invalid task type: {task_type_str}")
        sys.exit(1)

    # Simple argument parsing (extend as needed)
    if task_type == TaskType.CODE_GENERATION and "--spec" in sys.argv:
        spec_idx = sys.argv.index("--spec") + 1
        spec = sys.argv[spec_idx] if spec_idx < len(sys.argv) else ""
        result = router.generate_code(spec)
        print(json.dumps(result, indent=2))

    elif task_type == TaskType.CODE_ANALYSIS and "--code" in sys.argv:
        code_idx = sys.argv.index("--code") + 1
        code = sys.argv[code_idx] if code_idx < len(sys.argv) else ""
        result = router.analyze_code(code)
        print(json.dumps(result, indent=2))

    else:
        print("Insufficient arguments for task type")
        sys.exit(1)


if __name__ == "__main__":
    main()
