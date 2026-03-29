# OpenLlama - Maintenance & Developer Documentation

## Architecture Overview

OpenLlama is an autonomous AI coding agent that generates, tests, and debugs Python code using a local llama.cpp server. It follows a modular architecture with clear separation of concerns.

## Project Structure

```
open_llama/
├── __init__.py         # Package initialization, exports main classes
├── config.py           # Configuration management (OpenLlamaConfig)
├── llm.py              # LLM client for llama.cpp API communication
├── generator.py        # Code generation and file creation
├── runner.py           # Test execution and syntax validation
├── debugger.py         # Error handling and auto-debugging loop
├── store.py            # TinyDB persistence layer
├── main.py             # Main orchestrator (OpenLlama class)
├── setup.py           # Package setup for pip installation
├── requirements.txt   # Python dependencies
├── pytest.ini          # Pytest configuration
└── tests/             # Unit test suite
    ├── __init__.py
    ├── test_config.py
    ├── test_llm.py
    ├── test_generator.py
    ├── test_runner.py
    ├── test_debugger.py
    └── test_store.py
```

## Components

### 1. Configuration (`config.py`)

**Purpose**: Manages application configuration and provides defaults.

**Class**: `OpenLlamaConfig`

**Key Methods**:
- `from_file(path: str) -> OpenLlamaConfig`: Load config from JSON file
- `from_dict(data: dict) -> OpenLlamaConfig`: Create config from dictionary
- `ensure_output_dir() -> Path`: Create and return output directory
- `get_prompt_content() -> str`: Read prompt file content

**Configuration Fields**:
| Field | Type | Required | Default |
|-------|------|----------|---------|
| `api_url` | string | Yes | http://127.0.0.1:5000/v1/chat/completions |
| `prmpt_path` | string | Yes | prompt.txt |
| `folder` | string | Yes | output |

**Usage Example**:
```python
from config import OpenLlamaConfig

# From file
config = OpenLlamaConfig.from_file("config.json")

# From dictionary with defaults
config = OpenLlamaConfig.from_dict({
    "api_url": "http://localhost:8080/v1/chat",
    "prmpt_path": "my_prompt.txt",
    "folder": "generated"
})

# Ensure output directory exists
output_dir = config.ensure_output_dir()
```

---

### 2. LLM Client (`llm.py`)

**Purpose**: Handles communication with the llama.cpp server API.

**Class**: `LLMClient`

**Key Methods**:
- `__init__(api_url: str, model: str = "local-model")`: Initialize client
- `chat(prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 4096) -> str`: Send chat request
- `generate_code(task: str, context: Optional[str] = None) -> str`: Generate code with system prompt

**Error Handling**:
- `ConnectionError`: Cannot connect to llama.cpp server
- `ValueError`: Unexpected response format
- `RuntimeError`: General request failures

**Usage Example**:
```python
from llm import LLMClient

llm = LLMClient("http://127.0.0.1:5000/v1/chat/completions")

response = llm.chat(
    prompt="Write a hello world function",
    system_prompt="You are a Python expert"
)

code = llm.generate_code(
    task="Create a calculator module",
    context="Should support add, subtract, multiply, divide"
)
```

**API Contract**:
- Expects llama.cpp server to use OpenAI-compatible `/v1/chat/completions` endpoint
- Request format: OpenAI chat completions JSON
- Response format: OpenAI chat completions JSON

---

### 3. Code Generator (`generator.py`)

**Purpose**: Parses LLM output and creates Python files in the output directory.

**Class**: `CodeGenerator`

**Key Methods**:
- `__init__(llm_client: LLMClient, output_dir: Path)`: Initialize generator
- `parse_code_blocks(text: str) -> List[Tuple[str, str]]`: Extract code blocks with filenames
- `_generate_filename(code: str) -> str`: Generate appropriate filename from code content
- `create_files(code_content: str) -> List[Path]`: Create files from LLM output
- `generate_from_prompt(prompt: str) -> str`: Generate code from a prompt

**Filename Detection**:
- Looks for `filename:` declarations in markdown
- Falls back to: `main.py` for `def main()`, multiple functions with `__name__`
- Uses common module names: calculator, math, utils, api, client, server
- Defaults to first function/class name

**Usage Example**:
```python
from pathlib import Path
from llm import LLMClient
from generator import CodeGenerator

llm = LLMClient("http://127.0.0.1:5000/v1/chat/completions")
generator = CodeGenerator(llm, Path("output"))

# Generate from prompt
code = generator.generate_from_prompt("Create a calculator with add, subtract")

# Create files from existing code
files = generator.create_files(code)
# Returns list of Path objects for created files
```

---

### 4. Runner (`runner.py`)

**Purpose**: Executes Python files, runs tests, and validates syntax.

**Classes**: `ExecResult`, `Runner`

**ExecResult**:
- `success: bool`: Whether execution succeeded
- `output: str`: Standard output
- `error: Optional[str]`: Standard error

**Runner Key Methods**:
- `run_python_file(filepath: Path, args: List[str] = None) -> ExecResult`: Run a Python file
- `run_tests(test_dir: Optional[Path] = None) -> ExecResult`: Run pytest
- `check_syntax(filepath: Path) -> Tuple[bool, Optional[str]]`: Check single file syntax
- `check_all_syntax() -> Tuple[bool, List[str]]`: Check all Python files

**Timeouts**:
- Python file execution: 60 seconds
- Test execution: 120 seconds

**Usage Example**:
```python
from pathlib import Path
from runner import Runner, ExecResult

runner = Runner(Path("output"))

# Run main file
result = runner.run_python_file(Path("output/main.py"))
if result.success:
    print("Output:", result.output)
else:
    print("Error:", result.error)

# Run tests
test_result = runner.run_tests()
if test_result.success:
    print("All tests passed!")

# Check syntax
valid, errors = runner.check_all_syntax()
if not valid:
    print("Syntax errors:", errors)
```

---

### 5. Debugger (`debugger.py`)

**Purpose**: Automatically fixes code errors by sending them back to the LLM.

**Class**: `Debugger`

**Key Methods**:
- `__init__(llm_client: LLMClient, runner: Runner, output_dir: Path)`: Initialize
- `fix_error(error_message: str, context: str, iteration: int) -> Tuple[bool, str]`: Single fix attempt
- `debug_and_fix(error_message: str, context: str = "") -> Tuple[bool, str]`: Full debug loop
- `handle_syntax_errors(errors: List[str]) -> Tuple[bool, str]`: Fix syntax errors
- `handle_runtime_error(error: str, related_file: Optional[Path]) -> Tuple[bool, str]`: Fix runtime errors
- `handle_test_failure(test_output: str) -> Tuple[bool, str]`: Fix test failures

**Configuration**:
- `max_iterations`: Maximum debug attempts (default: 5)

**Debug Loop Flow**:
1. Receive error message and optional context
2. Send to LLM with debugging instructions
3. Receive fixed code
4. Apply fixes
5. Validate again
6. Repeat up to max_iterations

**Usage Example**:
```python
from pathlib import Path
from llm import LLMClient
from runner import Runner
from debugger import Debugger

llm = LLMClient("http://127.0.0.1:5000/v1/chat/completions")
runner = Runner(Path("output"))
debugger = Debugger(llm, runner, Path("output"))

# Handle syntax errors
fixed, response = debugger.handle_syntax_errors([
    "output/main.py: line 10: syntax error"
])

# Handle runtime error
fixed, response = debugger.handle_runtime_error(
    "NameError: name 'foo' is not defined",
    Path("output/main.py")
)

# Handle test failures
fixed, response = debugger.handle_test_failure("FAILED test_add")
```

---

### 6. Persistence (`store.py`)

**Purpose**: Provides lightweight database storage using TinyDB.

**Classes**: `ProgressDB`, `PRDStore`

**ProgressDB Key Methods**:
- `add_progress(story_id: str, description: str, files: list, learnings: list)`: Record progress
- `get_progress() -> list`: Retrieve all progress entries
- `add_learning(category: str, content: str)`: Store reusable learnings
- `get_learnings() -> list`: Retrieve learnings
- `save_state(key: str, value: Any)`: Save key-value state
- `get_state(key: str, default: Any = None) -> Any`: Retrieve state
- `mark_story_complete(story_id: str)`: Mark PRD story complete
- `is_story_complete(story_id: str) -> bool`: Check completion status

**Database Tables**:
1. **progress**: Tracks generated files and learnings per story
2. **state**: Key-value store for application state
3. **learnings**: Reusable knowledge from debugging sessions

**PRDStore Key Methods**:
- `save_prd(prd_data: Dict)`: Store PRD document
- `get_prd() -> Optional[Dict]`: Retrieve PRD
- `update_story_status(story_id: str, passes: bool)`: Update story completion
- `get_next_story() -> Optional[Dict]`: Get highest priority incomplete story

**Usage Example**:
```python
from pathlib import Path
from store import ProgressDB, PRDStore

db = ProgressDB(Path("output/open_llama_db.json"))

# Track progress
db.add_progress("US-001", "Create calculator", ["main.py", "calculator.py"], [])

# Store learnings
db.add_learning("error_handling", "Always validate input parameters")

# PRD workflow
prd_store = PRDStore(db)
prd_store.save_prd(prd_data)
story = prd_store.get_next_story()
prd_store.update_story_status("US-001", True)

db.close()
```

---

### 7. Main Orchestrator (`main.py`)

**Purpose**: Coordinates all components and provides CLI interface.

**Class**: `OpenLlama`

**Key Methods**:
- `__init__(config: OpenLlamaConfig)`: Initialize with config
- `run_prompt_mode(prompt_file: str) -> bool`: Process prompt file
- `run_prd_mode(prd_file: str) -> bool`: Process PRD file
- `test_and_debug_loop(files: list, max_iterations: int = 10) -> bool`: Test and debug cycle
- `close()`: Close database connections

**Usage Example**:
```python
from config import OpenLlamaConfig
from main import OpenLlama

config = OpenLlamaConfig(
    api_url="http://127.0.0.1:5000/v1/chat/completions",
    prmpt_path="prompt.txt",
    folder="output"
)

open_llama = OpenLlama(config)

try:
    success = open_llama.run_prompt_mode("prompt.txt")
finally:
    open_llama.close()
```

---

## Configuration Fields Reference

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `api_url` | string | Yes | http://127.0.0.1:5000/v1/chat/completions | llama.cpp server URL |
| `prmpt_path` | string | Yes | prompt.txt | Path to prompt file |
| `folder` | string | Yes | output | Output directory for generated files |

## Database Schema

### Progress Table
```python
{
    "story_id": str,           # Unique story identifier
    "description": str,         # Story description
    "files": list,             # List of created file paths
    "learnings": list,         # List of learnings
    "timestamp": str           # ISO format timestamp
}
```

### State Table
```python
{
    "key": str,                # State key
    "value": any              # State value
}
```

### Learnings Table
```python
{
    "category": str,           # Learning category
    "content": str,           # Learning content
    "timestamp": str          # ISO format timestamp
}
```

## Extending OpenLlama

### Adding New LLM Providers

To add support for different LLM backends, subclass `LLMClient`:

```python
from llm import LLMClient

class CustomLLMClient(LLMClient):
    def __init__(self, api_url: str, api_key: str = None):
        super().__init__(api_url)
        self.api_key = api_key
    
    def chat(self, prompt: str, system_prompt: str = None, max_tokens: int = 4096) -> str:
        # Implement custom API call
        # Return the response text
        pass
```

### Adding Test Frameworks

Extend `Runner` class to support additional test frameworks:

```python
from runner import Runner, ExecResult

class CustomRunner(Runner):
    def run_tests(self, test_dir: Path = None) -> ExecResult:
        # Add support for unittest, nose2, etc.
        pass
    
    def run_npm_tests(self) -> ExecResult:
        # Support JavaScript/TypeScript projects
        pass
```

### Custom Debug Strategies

Modify `Debugger` class to implement different debugging approaches:

```python
from debugger import Debugger

class CustomDebugger(Debugger):
    def fix_error(self, error_message: str, context: str, iteration: int) -> Tuple[bool, str]:
        # Implement custom fixing logic
        # Could use different prompts, retry logic, etc.
        pass
```

### Adding New File Types

To support generating other file types (JavaScript, TypeScript, etc.):

```python
from generator import CodeGenerator

class MultiLanguageGenerator(CodeGenerator):
    def parse_code_blocks(self, text: str, language: str = "python"):
        # Handle different language blocks
        pass
    
    def create_files(self, code_content: str, language: str = "python"):
        # Create appropriate file extensions
        pass
```

## Testing

Run the test suite:

```bash
pytest open_llama/tests/ -v
```

Run specific test file:

```bash
pytest open_llama/tests/test_config.py -v
```

Run with coverage:

```bash
pytest open_llama/tests/ --cov=open_llama --cov-report=html
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| requests | >=2.28.0 | HTTP client for LLM API |
| tinydb | >=4.7.0 | Lightweight JSON database |

## Version History

### 1.0.0
- Initial implementation
- llama.cpp server support
- Prompt and PRD modes
- TinyDB persistence
- Debug loop with configurable iterations

---

For usage documentation, see [USAGE.md](USAGE.md).
