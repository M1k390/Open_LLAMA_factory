"""Tests for runner module."""

import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch
from runner import Runner


class TestRunner:
    def test_run_python_file_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = Runner(Path(tmpdir))
            
            test_file = Path(tmpdir) / "test_script.py"
            test_file.write_text("print('hello')")
            
            result = runner.run_python_file(test_file)
            
            assert result.success is True
            assert "hello" in result.output

    def test_run_python_file_with_args(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = Runner(Path(tmpdir))
            
            test_file = Path(tmpdir) / "test_args.py"
            test_file.write_text("import sys; print(sys.argv[1])")
            
            result = runner.run_python_file(test_file, args=["world"])
            
            assert result.success is True
            assert "world" in result.output

    def test_run_python_file_syntax_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = Runner(Path(tmpdir))
            
            test_file = Path(tmpdir) / "bad_syntax.py"
            test_file.write_text("def bad(: # syntax error")
            
            result = runner.run_python_file(test_file)
            
            assert result.success is False
            assert result.error is not None

    def test_check_syntax_valid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = Runner(Path(tmpdir))
            
            test_file = Path(tmpdir) / "valid.py"
            test_file.write_text("def valid(): pass")
            
            valid, error = runner.check_syntax(test_file)
            
            assert valid is True
            assert error is None

    def test_check_syntax_invalid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = Runner(Path(tmpdir))
            
            test_file = Path(tmpdir) / "invalid.py"
            test_file.write_text("def bad(: pass")
            
            valid, error = runner.check_syntax(test_file)
            
            assert valid is False
            assert error is not None

    def test_check_all_syntax_all_valid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = Runner(Path(tmpdir))
            
            (Path(tmpdir) / "file1.py").write_text("def a(): pass")
            (Path(tmpdir) / "file2.py").write_text("def b(): pass")
            
            valid, errors = runner.check_all_syntax()
            
            assert valid is True
            assert len(errors) == 0

    def test_check_all_syntax_with_errors(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = Runner(Path(tmpdir))
            
            (Path(tmpdir) / "valid.py").write_text("def good(): pass")
            (Path(tmpdir) / "invalid.py").write_text("def bad(: pass")
            
            valid, errors = runner.check_all_syntax()
            
            assert valid is False
            assert len(errors) == 1
            assert "invalid.py" in errors[0]


class TestExecResult:
    def test_success_result(self):
        from runner import ExecResult
        result = ExecResult(True, "output here", None)
        assert result.success is True
        assert result.output == "output here"
        assert result.error is None

    def test_failure_result(self):
        from runner import ExecResult
        result = ExecResult(False, "partial output", "error message")
        assert result.success is False
        assert result.output == "partial output"
        assert result.error == "error message"
