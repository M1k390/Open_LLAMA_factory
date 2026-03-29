"""Tests for generator module."""

import tempfile
from pathlib import Path
from unittest.mock import Mock
from generator import CodeGenerator


class TestCodeGenerator:
    def test_parse_code_blocks_simple(self):
        mock_llm = Mock()
        gen = CodeGenerator(mock_llm, Path("/tmp"))
        
        text = '''
Here is the code:

```python
def hello():
    return "world"
```

That's it!
'''
        blocks = gen.parse_code_blocks(text)
        assert len(blocks) == 1
        assert 'def hello' in blocks[0][1]

    def test_parse_code_blocks_with_filename(self):
        mock_llm = Mock()
        gen = CodeGenerator(mock_llm, Path("/tmp"))
        
        text = '''
filename: test_module.py
```python
def test_func():
    pass
```
'''
        blocks = gen.parse_code_blocks(text)
        assert len(blocks) >= 1

    def test_generate_filename_from_def(self):
        mock_llm = Mock()
        gen = CodeGenerator(mock_llm, Path("/tmp"))
        
        code = '''
def calculate_total():
    return 100
'''
        filename = gen._generate_filename(code)
        assert filename == "calculate_total.py"

    def test_generate_filename_from_class(self):
        mock_llm = Mock()
        gen = CodeGenerator(mock_llm, Path("/tmp"))
        
        code = '''
class MyClass:
    pass
'''
        filename = gen._generate_filename(code)
        assert filename == "myclass.py"

    def test_generate_filename_main(self):
        mock_llm = Mock()
        gen = CodeGenerator(mock_llm, Path("/tmp"))
        
        code = '''
def main():
    pass
'''
        filename = gen._generate_filename(code)
        assert filename == "main.py"

    def test_create_files(self):
        mock_llm = Mock()
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = CodeGenerator(mock_llm, Path(tmpdir))
            
            code = '''
```python
def hello():
    return "world"
```
'''
            files = gen.create_files(code)
            
            assert len(files) == 1
            assert files[0].name == "hello.py"
            assert files[0].read_text() == 'def hello():\n    return "world"'

    def test_create_files_with_path(self):
        mock_llm = Mock()
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = CodeGenerator(mock_llm, Path(tmpdir))
            
            code = '''
filename: subdir/myfile.py
```python
def func():
    pass
```
'''
            files = gen.create_files(code)
            
            assert len(files) == 1
            assert files[0].name == "myfile.py"
            assert files[0].parent.name == "subdir"
