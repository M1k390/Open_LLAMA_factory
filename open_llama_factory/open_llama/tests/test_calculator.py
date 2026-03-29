"""Tests for calculator.py (generated output)."""

import sys
from pathlib import Path

test_dir = Path('/home/minisforum/Workspace/test_open_llama')
sys.path.insert(0, str(test_dir))

from main import add, subtract, multiply, divide


class TestCalculator:
    def test_add(self):
        assert add(5, 3) == 8
        assert add(-2, 8) == 6
        assert add(-5, -3) == -8
        assert add(0, 0) == 0

    def test_subtract(self):
        assert subtract(5, 3) == 2
        assert subtract(-2, 8) == -10
        assert subtract(-5, -3) == -2
        assert subtract(0, 0) == 0

    def test_multiply(self):
        assert multiply(5, 3) == 15
        assert multiply(-2, 8) == -16
        assert multiply(-5, -3) == 15
        assert multiply(0, 100) == 0

    def test_divide(self):
        assert divide(6, 2) == 3
        assert divide(-10, 2) == -5
        assert divide(5, 2) == 2.5
        assert divide(0, 5) == 0

    def test_divide_by_zero(self):
        with __import__('pytest').raises(ValueError) as exc_info:
            divide(5, 0)
        assert "zero" in str(exc_info.value).lower()
