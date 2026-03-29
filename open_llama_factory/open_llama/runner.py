"""Test runner and result handling."""

import subprocess
import sys
from pathlib import Path
from typing import Tuple, Optional, List


class ExecResult:
    def __init__(self, success: bool, output: str, error: Optional[str] = None):
        self.success = success
        self.output = output
        self.error = error


class Runner:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def run_python_file(self, filepath: Path, args: List[str] = None) -> ExecResult:
        """Run a Python file and return the result."""
        cmd = [sys.executable, str(filepath)]
        if args:
            cmd.extend(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.output_dir
            )
            
            if result.returncode == 0:
                return ExecResult(True, result.stdout)
            else:
                return ExecResult(False, result.stdout, result.stderr)
        
        except subprocess.TimeoutExpired:
            return ExecResult(False, "", "Execution timed out after 60 seconds")
        except Exception as e:
            return ExecResult(False, "", str(e))

    def run_tests(self, test_dir: Optional[Path] = None) -> ExecResult:
        """Run pytest tests in the output directory."""
        if test_dir is None:
            test_dir = self.output_dir
        
        cmd = [sys.executable, "-m", "pytest", str(test_dir), "-v"]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.output_dir
            )
            
            if result.returncode == 0:
                return ExecResult(True, result.stdout)
            else:
                return ExecResult(False, result.stdout, result.stderr)
        
        except FileNotFoundError:
            return ExecResult(False, "", "pytest not installed")
        except subprocess.TimeoutExpired:
            return ExecResult(False, "", "Tests timed out after 120 seconds")
        except Exception as e:
            return ExecResult(False, "", str(e))

    def check_syntax(self, filepath: Path) -> Tuple[bool, Optional[str]]:
        """Check Python syntax of a file."""
        cmd = [sys.executable, "-m", "py_compile", str(filepath)]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return True, None
            return False, result.stderr
        except Exception as e:
            return False, str(e)

    def check_all_syntax(self) -> Tuple[bool, List[str]]:
        """Check syntax of all Python files in output directory."""
        errors = []
        py_files = list(self.output_dir.rglob("*.py"))
        
        for filepath in py_files:
            valid, error = self.check_syntax(filepath)
            if not valid:
                errors.append(f"{filepath}: {error}")
        
        return len(errors) == 0, errors
