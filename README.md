# Open Llama Factory

An AI-based autonomous programming agent that uses a local llama.cpp server to automatically generate, test, and debug Python software.

The project was born for study and fun; I want to share it to help it grow.
The concept arose from the problem of being unable to find a **free** code generation agent that works well with llama.cpp.
This software was created to solve this problem.
The software works, but it's still rough and needs improvement.

## Features

- **Automatic Code Generation**: Describe what you want in plain English, and OpenLlama generates the complete Python code
- **Self-Testing**: Automatically runs generated code to verify it works
- **Auto-Debugging**: Detects and fixes errors by sending them back to the LLM
- **PRD Mode**: Works with Product Requirements Documents (JSON format) for feature-driven development
- **Local & Private**: Runs entirely on your local machine with llama.cpp - no cloud APIs needed
- **Persistent State**: Uses TinyDB to track progress and learnings across runs

## Requirements

- Python 3.8+
- Local llama.cpp server running
- Dependencies: `requests`, `tinydb`

## Quick Start

### 1. Install Dependencies

```bash
cd open_llama
pip install -e .
```

Or install dependencies directly:
```bash
pip install requests tinydb pytest
```

### 2. Start llama.cpp Server

```bash
# Example - adjust path to your model
./server -m model.gguf -host 127.0.0.1 -port 5000
```

### 3. Create a Prompt

Create a `prompt.txt` file describing the software:

```
Create a simple calculator module with add, subtract, multiply, divide functions.
Include a main() function that demonstrates all operations.
```

### 4. Run OpenLlama

```bash
python -m open_llama.main --prompt prompt.txt --output generated/
```

## Configuration

Create a `config.json` file:

```json
{
    "api_url": "http://127.0.0.1:5000/v1/chat/completions",
    "prmpt_path": "prompt.txt",
    "folder": "output"
}
```

| Field | Description | Default |
|-------|-------------|---------|
| `api_url` | URL of llama.cpp server | http://127.0.0.1:5000/v1/chat/completions |
| `prmpt_path` | Path to prompt file | prompt.txt |
| `folder` | Output directory | output |

## Usage Modes

### Prompt Mode (Recommended)

```bash
python -m open_llama.main --prompt prompt.txt
python -m open_llama.main --prompt prompt.txt --output myapp/
python -m open_llama.main --prompt prompt.txt --api-url http://localhost:8080/v1/chat/completions
```

### PRD Mode

For feature-driven development using Product Requirements Documents:

```bash
python -m open_llama.main --prd prd.json
```

See [PRD Format](#prd-format) for details.

## PRD Format

```json
{
    "project": "Project Name",
    "branchName": "feature/branch-name",
    "description": "Project description",
    "userStories": [
        {
            "id": "US-001",
            "title": "User can do something",
            "description": "Description of the feature",
            "acceptanceCriteria": ["Criterion 1", "Criterion 2"],
            "priority": 1,
            "passes": false,
            "notes": ""
        }
    ]
}
```

## How It Works

1. **Read Prompt**: Reads the prompt file describing desired software
2. **Generate Code**: Sends prompt to llama.cpp server, receives Python code
3. **Create Files**: Writes generated code to the output directory
4. **Validate Syntax**: Checks all Python files for syntax errors
5. **Run Code**: Executes the main Python file
6. **Run Tests**: Runs pytest if tests exist
7. **Auto-Debug**: If errors occur, sends them back to LLM for fixes
8. **Repeat**: Continues until code works or max iterations (10) reached

## Command Line Options

| Option | Description |
|--------|-------------|
| `--config`, `-c` | Path to configuration file |
| `--prompt`, `-p` | Path to prompt file |
| `--prd` | Path to PRD JSON file |
| `--api-url` | Override API URL |
| `--output`, `-o` | Override output folder |

## Exit Codes

- `0`: Success - all tasks completed
- `1`: Failure - errors occurred

## Architecture

OpenLlama follows a modular architecture:

```
open_llama/
├── __init__.py       # Package initialization
├── config.py         # Configuration management
├── llm.py           # LLM client for llama.cpp
├── generator.py     # Code generation logic
├── runner.py        # Test execution
├── debugger.py      # Debug loop
├── store.py         # TinyDB persistence
├── main.py          # Main orchestrator
├── setup.py         # Package setup
├── requirements.txt # Dependencies
└── tests/          # Unit tests
```

See [MAINTENANCE.md](MAINTENANCE.md) for detailed component documentation.

## Testing

```bash
pytest open_llama/tests/ -v
```

## Troubleshooting

### Cannot connect to llama.cpp server

Ensure your llama.cpp server is running:
```bash
./server -m model.gguf -host 127.0.0.1 -port 5000
```

### Infinite loop in debugging

**Open Llama Factory** limits debug iterations to 10 by default. If code keeps failing:
- Review the generated code manually
- Simplify your prompt
- Break down complex tasks into smaller prompts

## License
**Open LLAMA Factory** is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

**Open LLAMA Factory** is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see
<http://www.gnu.org/licenses/>.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
