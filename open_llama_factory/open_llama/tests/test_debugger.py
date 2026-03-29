"""Tests for debugger module."""

import tempfile
from pathlib import Path
from unittest.mock import Mock
from debugger import Debugger
from runner import Runner


class TestDebugger:
    def test_init(self):
        mock_llm = Mock()
        mock_runner = Mock()
        with tempfile.TemporaryDirectory() as tmpdir:
            debugger = Debugger(mock_llm, mock_runner, Path(tmpdir))
            
            assert debugger.llm == mock_llm
            assert debugger.runner == mock_runner
            assert debugger.max_iterations == 5

    def test_fix_error(self):
        mock_llm = Mock()
        mock_llm.chat.return_value = "Fixed code here"
        mock_runner = Mock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            debugger = Debugger(mock_llm, mock_runner, Path(tmpdir))
            
            success, response = debugger.fix_error("Error message", "Context", 1)
            
            assert success is True
            assert response == "Fixed code here"
            mock_llm.chat.assert_called_once()

    def test_fix_error_max_iterations(self):
        mock_llm = Mock()
        mock_runner = Mock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            debugger = Debugger(mock_llm, mock_runner, Path(tmpdir))
            
            success, response = debugger.fix_error("Error", "Context", 6)
            
            assert success is False
            assert "Max debug iterations" in response
            mock_llm.chat.assert_not_called()

    def test_debug_and_fix_iterates_correctly(self):
        mock_llm = Mock()
        mock_llm.chat.return_value = "Fixed code"
        mock_runner = Mock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            debugger = Debugger(mock_llm, mock_runner, Path(tmpdir))
            debugger.max_iterations = 3
            
            success, response = debugger.debug_and_fix("Error", "Context")
            
            assert mock_llm.chat.call_count == 3

    def test_debug_and_fix_max_attempts(self):
        mock_llm = Mock()
        mock_llm.chat.return_value = "Still broken"
        mock_runner = Mock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            debugger = Debugger(mock_llm, mock_runner, Path(tmpdir))
            debugger.max_iterations = 2
            
            success, response = debugger.debug_and_fix("Error", "Context")
            
            assert success is False
            assert mock_llm.chat.call_count == 2

    def test_handle_syntax_errors(self):
        mock_llm = Mock()
        mock_llm.chat.return_value = "Fixed syntax"
        mock_runner = Mock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            debugger = Debugger(mock_llm, mock_runner, Path(tmpdir))
            
            success, response = debugger.handle_syntax_errors(
                ["file.py: syntax error"]
            )
            
            assert mock_llm.chat.called

    def test_handle_runtime_error(self):
        mock_llm = Mock()
        mock_llm.chat.return_value = "Fixed runtime"
        mock_runner = Mock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            debugger = Debugger(mock_llm, mock_runner, Path(tmpdir))
            
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def test(): pass")
            
            success, response = debugger.handle_runtime_error(
                "RuntimeError occurred",
                test_file
            )
            
            assert mock_llm.chat.called

    def test_handle_test_failure(self):
        mock_llm = Mock()
        mock_llm.chat.return_value = "Fixed tests"
        mock_runner = Mock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            debugger = Debugger(mock_llm, mock_runner, Path(tmpdir))
            
            success, response = debugger.handle_test_failure("Test output")
            
            assert mock_llm.chat.called
