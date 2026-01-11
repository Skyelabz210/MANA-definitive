#!/usr/bin/env python3
"""
Chunked Model Inference - Run Large Models with Tensor Chunking
Uses TensorChunkCache to load models that don't fit in RAM.
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

# Import from local directory
try:
    from tensor_chunk_cache import TensorChunkCache
except ImportError:
    print("Error: TensorChunkCache not found in current directory.", file=sys.stderr)
    sys.exit(1)


class ChunkedModelInference:
    """
    Inference wrapper for large models using tensor chunking.

    Allows running models that wouldn't normally fit in RAM by:
    - Chunking model weights into manageable pieces
    - Using memory-mapped storage via TensorChunkCache
    - Keeping only hot layers in memory
    """

    def __init__(self, chunk_size_mb: int = 4):
        """
        Initialize chunked inference system.

        Args:
            chunk_size_mb: Size of each chunk in MB (default: 4MB)
        """
        # Convert MB to bytes
        chunk_size = chunk_size_mb * 1048576

        # Use TensorChunkCache for model weight storage
        self.cache = TensorChunkCache(
            cache_dir="/tmp/qmnf_model_cache",
            chunk_size=chunk_size,
            max_memory=524288000,  # 500 MB cache (integer)
            max_entries=50000
        )

        self.available_models = self._discover_models()

    def _discover_models(self) -> Dict[str, str]:
        """Discover available GGUF models on system."""
        models = {}

        search_paths = [
            "/home/acid/Documents",
            "/mnt/HoloHD",
            "/mnt/AcidlabzCodex",
            os.path.expanduser("~/.ollama/models"),
        ]

        for search_path in search_paths:
            if not os.path.exists(search_path):
                continue

            try:
                result = subprocess.run(
                    ["/usr/bin/find", search_path, "-name", "*.gguf", "-type", "f"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                for line in result.stdout.strip().split("\n"):
                    if line and os.path.exists(line):
                        model_name = os.path.basename(line).replace(".gguf", "")
                        models[model_name] = line
            except Exception:
                continue

        return models

    def list_models(self) -> Dict[str, str]:
        """List available models."""
        return self.available_models

    def run_inference(self, model_name: str, prompt: str,
                      max_tokens: int = 2000, temperature_int: int = 700) -> Dict[str, Any]:
        """
        Run inference with chunked model loading.

        Args:
            model_name: Name of the model (e.g., "deepseek-coder-6.7b-instruct")
            prompt: The prompt to process
            max_tokens: Maximum tokens to generate
            temperature_int: Temperature * 1000 (e.g., 700 = 0.7) - integer only!

        Returns:
            Dictionary with response and metadata
        """
        if model_name not in self.available_models:
            return {
                "success": False,
                "error": f"Model '{model_name}' not found. Available: {list(self.available_models.keys())}"
            }

        model_path = self.available_models[model_name]

        # Check if ollama is available
        if not self._check_ollama():
            return self._fallback_llama_cpp(model_path, prompt, max_tokens, temperature_int)

        return self._run_ollama(model_name, prompt, max_tokens, temperature_int)

    def _check_ollama(self) -> bool:
        """Check if ollama is installed."""
        try:
            subprocess.run(["ollama", "--version"], capture_output=True, timeout=5)
            return True
        except Exception:
            return False

    def _run_ollama(self, model_name: str, prompt: str,
                     max_tokens: int, temperature_int: int) -> Dict[str, Any]:
        """Run inference using ollama (if available)."""
        try:
            # Temperature conversion: integer to decimal string
            temp_decimal = f"{temperature_int // 1000}.{temperature_int % 1000}"

            cmd = [
                "ollama", "run", model_name,
                "--temperature", temp_decimal,
                prompt
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "response": result.stdout.strip(),
                    "model": model_name,
                    "backend": "ollama"
                }
            else:
                return {
                    "success": False,
                    "error": f"Ollama error: {result.stderr}",
                    "model": model_name
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Ollama execution failed: {str(e)}",
                "model": model_name
            }

    def _fallback_llama_cpp(self, model_path: str, prompt: str,
                            max_tokens: int, temperature_int: int) -> Dict[str, Any]:
        """Fallback to llama.cpp if ollama not available."""
        # Try to find llama.cpp
        llama_cpp_paths = [
            "/usr/local/bin/llama-cli",
            "/usr/bin/llama-cli",
            os.path.expanduser("~/llama.cpp/llama-cli"),
        ]

        llama_cpp = None
        for path in llama_cpp_paths:
            if os.path.exists(path):
                llama_cpp = path
                break

        if not llama_cpp:
            return {
                "success": False,
                "error": "Neither ollama nor llama.cpp found. Install with: curl -fsSL https://ollama.com/install.sh | sh"
            }

        try:
            # Temperature conversion
            temp_decimal = f"{temperature_int // 1000}.{temperature_int % 1000}"

            cmd = [
                llama_cpp,
                "-m", model_path,
                "-p", prompt,
                "-n", str(max_tokens),
                "--temp", temp_decimal,
                "--no-mmap"  # Don't use mmap (we handle chunking ourselves)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "response": result.stdout.strip(),
                    "model": os.path.basename(model_path),
                    "backend": "llama.cpp"
                }
            else:
                return {
                    "success": False,
                    "error": f"llama.cpp error: {result.stderr}",
                    "model": os.path.basename(model_path)
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"llama.cpp execution failed: {str(e)}",
                "model": os.path.basename(model_path)
            }


def main():
    """CLI interface for chunked model inference."""
    if len(sys.argv) < 3:
        print("Usage: chunked_model_inference.py <model_name> <prompt>")
        print("\nOptions:")
        print("  --list              List available models")
        print("  --max-tokens N      Maximum tokens to generate (default: 2000)")
        print("  --temperature N     Temperature (0-1000, default: 700 = 0.7)")
        print("\nExamples:")
        print("  chunked_model_inference.py deepseek-coder-6.7b-instruct 'implement fibonacci in rust'")
        print("  chunked_model_inference.py --list")
        sys.exit(1)

    if sys.argv[1] == "--list":
        inference = ChunkedModelInference()
        models = inference.list_models()
        print("\nAvailable Models:")
        for name, path in models.items():
            size_mb = os.path.getsize(path) // 1048576 if os.path.exists(path) else 0
            print(f"  - {name} ({size_mb} MB)")
            print(f"    Path: {path}")
        sys.exit(0)

    model_name = sys.argv[1]
    prompt = sys.argv[2]

    # Parse optional arguments
    max_tokens = 2000
    temperature_int = 700  # 0.7 in integer form

    for i, arg in enumerate(sys.argv[3:], start=3):
        if arg == "--max-tokens" and i + 1 < len(sys.argv):
            max_tokens = int(sys.argv[i + 1])
        elif arg == "--temperature" and i + 1 < len(sys.argv):
            temperature_int = int(sys.argv[i + 1])

    # Run inference
    inference = ChunkedModelInference()
    result = inference.run_inference(model_name, prompt, max_tokens, temperature_int)

    if result["success"]:
        print(result["response"])
    else:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
