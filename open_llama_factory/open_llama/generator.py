"""Code generator using LLM."""

import re
from pathlib import Path
from typing import List, Dict, Tuple
from llm import LLMClient


class CodeGenerator:
    def __init__(self, llm_client: LLMClient, output_dir: Path):
        self.llm = llm_client
        self.output_dir = output_dir

    def parse_code_blocks(self, text: str) -> List[Tuple[str, str]]:
        """Extract code blocks with their filenames from LLM output."""
        blocks = []
        lines = text.split('\n')
        current_filename = None
        current_code = []
        in_code_block = False

        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith('```') and not in_code_block:
                in_code_block = True
                current_code = []
                if current_filename is None:
                    idx = lines.index(line)
                    for j in range(max(0, idx-2), idx):
                        prev = lines[j].strip()
                        if prev.startswith('filename:'):
                            current_filename = prev.replace('filename:', '').strip().strip('`').strip()
                            break
                continue
            
            if stripped.startswith('```') and in_code_block:
                in_code_block = False
                if current_code:
                    code = '\n'.join(current_code).strip()
                    if code and not code.startswith('# ') and not code.startswith('filename'):
                        blocks.append((current_filename, code))
                current_filename = None
                current_code = []
                continue
            
            if in_code_block:
                current_code.append(line)

        if in_code_block and current_code:
            code = '\n'.join(current_code).strip()
            if code:
                blocks.append((current_filename, code))

        pattern = r'```(?:python|py)?\s*\n([\s\S]*?)```'
        for match in re.findall(pattern, text):
            code = match.strip()
            if code and len(code) > 10:
                code_lines = [l for l in code.split('\n') if not l.strip().startswith('filename')]
                clean_code = '\n'.join(code_lines).strip()
                if clean_code and not any(clean_code in b[1] for b in blocks):
                    if 'def ' in clean_code or 'class ' in clean_code:
                        blocks.append((None, clean_code))

        return blocks

    def _generate_filename(self, code: str) -> str:
        """Generate a filename based on code content."""
        if 'def main(' in code:
            return "main.py"
        
        has_multiple_funcs = code.count('def ') > 1 or ('class ' in code and 'def ' in code)
        if has_multiple_funcs and '__name__' in code:
            return "main.py"
        
        common_modules = ['calculator', 'math', 'utils', 'helpers', 'api', 'client', 'server']
        for module in common_modules:
            if f'def {module}' in code or f'class {module.title()}' in code:
                return f"{module}.py"
        
        match = re.search(r'^(?:def|class)\s+(\w+)', code, re.MULTILINE)
        if match:
            name = match.group(1).lower()
            return f"{name}.py"
        return "main.py"

    def create_files(self, code_content: str) -> List[Path]:
        """Create Python files from LLM output."""
        created_files = []
        blocks = self.parse_code_blocks(code_content)
        
        for filename, code in blocks:
            if filename is None:
                filename = self._generate_filename(code)
            
            if not filename.endswith('.py'):
                filename = filename + '.py'
            
            filepath = self.output_dir / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, "w") as f:
                f.write(code)
            
            created_files.append(filepath)
        
        return created_files

    def generate_from_prompt(self, prompt: str) -> str:
        """Generate code from a prompt description."""
        
        system_prompt = """You are an expert Python developer. Generate complete Python code files.

CRITICAL RULES:
1. Your response must ONLY contain code in properly formatted markdown blocks
2. Do NOT include explanations, comments like "filename:", or placeholder text
3. The main() function MUST handle any exceptions gracefully (use try/except)
4. If a function raises ValueError, the main() must catch and display it
5. Write ONLY the actual Python code, nothing else

Example calculator with proper error handling:

```python
def add(a: float, b: float) -> float:
    return a + b

def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def main():
    print("Testing divide by 2:", divide(10, 2))
    try:
        print("Testing divide by 0:", divide(10, 0))
    except ValueError as e:
        print(f"Caught error: {e}")

if __name__ == "__main__":
    main()
```

Write ONLY the complete, working Python code inside code blocks."""
        
        user_prompt = f"""Create Python code for the following requirement:

{prompt}

Return the code in a markdown code block."""
        
        return self.llm.chat(user_prompt, system_prompt)
