"""Debugging loop for fixing code issues."""

from pathlib import Path
from typing import Tuple, Optional, List
from llm import LLMClient
from runner import Runner


class Debugger:
    def __init__(self, llm_client: LLMClient, runner: Runner, output_dir: Path):
        self.llm = llm_client
        self.runner = runner
        self.output_dir = output_dir
        self.max_iterations = 5

    def fix_error(self, error_message: str, context: str, iteration: int = 1) -> Tuple[bool, str]:
        """Attempt to fix an error by sending it back to the LLM."""
        if iteration > self.max_iterations:
            return False, "Max debug iterations reached"

        system_prompt = """You are an expert Python debugger. Fix the error and provide corrected code.
        
        Rules:
        1. Analyze the error carefully
        2. Fix the root cause, not just the symptoms
        3. Provide complete, corrected code blocks
        4. Use markdown code blocks with filename headers
        5. Explain what was wrong and how you fixed it"""
        
        user_prompt = f"""The following error occurred:

{error_message}

Context (current code or recent changes):
{context}

Please fix this error and provide the corrected code."""
        
        response = self.llm.chat(user_prompt, system_prompt)
        return True, response

    def debug_and_fix(self, error_message: str, context: str = "") -> Tuple[bool, str]:
        """Debug loop: try to fix errors up to max_iterations times."""
        current_context = context
        
        for i in range(1, self.max_iterations + 1):
            success, response = self.fix_error(error_message, current_context, i)
            
            if not success:
                return False, response
            
            current_context = f"Previous fix attempt:\n{response}\n\nOriginal error:\n{error_message}"
        
        return False, "Could not fix error after maximum iterations"

    def handle_syntax_errors(self, errors: List[str]) -> Tuple[bool, str]:
        """Handle syntax errors by fixing them."""
        error_summary = "\n".join(errors)
        return self.debug_and_fix(
            f"Syntax errors found:\n{error_summary}",
            "Code has syntax errors that prevent it from running"
        )

    def handle_runtime_error(self, error: str, related_file: Optional[Path] = None) -> Tuple[bool, str]:
        """Handle runtime errors."""
        context = ""
        if related_file and related_file.exists():
            with open(related_file, "r") as f:
                context = f.read()
        
        return self.debug_and_fix(f"Runtime error:\n{error}", context)

    def handle_test_failure(self, test_output: str) -> Tuple[bool, str]:
        """Handle test failures."""
        return self.debug_and_fix(
            f"Tests failed:\n{test_output}",
            "Test suite is failing"
        )
