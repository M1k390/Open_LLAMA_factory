# OpenLlama - Usage Documentation

OpenLlama is an autonomous AI coding agent that uses a local llama.cpp server to generate, test, and debug Python software automatically.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage Modes](#usage-modes)
5. [Command Line Options](#command-line-options)
6. [How It Works](#how-it-works)
7. [PRD Format](#prd-format)
8. [Examples](#examples)
9. [Exit Codes](#exit-codes)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

- **Python 3.8+**: Required to run OpenLlama
- **llama.cpp server**: Must be running locally with OpenAI-compatible API
- **Python packages**: `requests`, `tinydb`

### Setting Up llama.cpp Server

1. Clone and build llama.cpp:
```bash
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
make
```

2. Start the server:
```bash
./server -m model.gguf -c 2048 -host 127.0.0.1 -port 5000
```

The server should be accessible at: `http://127.0.0.1:5000/v1/chat/completions`

## Installation

### Option 1: Install as Package

```bash
cd open_llama
pip install -e .
```

### Option 2: Install Dependencies Only

```bash
pip install requests tinydb pytest
```

### Option 3: Using Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate    # Windows

pip install requests tinydb pytest
```

## Configuration

### Configuration File

Create a `config.json` file in your project:

```json
{
    "api_url": "http://127.0.0.1:5000/v1/chat/completions",
    "prmpt_path": "prompt.txt",
    "folder": "output"
}
```

### Configuration Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `api_url` | string | Yes | http://127.0.0.1:5000/v1/chat/completions | URL of llama.cpp server |
| `prmpt_path` | string | Yes | prompt.txt | Path to prompt file |
| `folder` | string | Yes | output | Output directory for generated files |

### Environment Variables

You can also override configuration via command line (see below).

## Usage Modes

### Prompt Mode (Recommended)

This is the simplest way to use OpenLlama. Create a prompt describing the software you want to build.

```bash
python -m open_llama.main --prompt prompt.txt
```

With custom output directory:

```bash
python -m open_llama.main --prompt prompt.txt --output myapp/
```

### PRD Mode

For feature-driven development using Product Requirements Documents:

```bash
python -m open_llama.main --prd prd.json
```

This mode processes user stories from the PRD sequentially, testing each one.

### Configuration Override

Override specific settings via command line:

```bash
python -m open_llama.main \
    --config config.json \
    --api-url http://localhost:8080/v1/chat/completions \
    --output generated/
```

## Command Line Options

| Option | Alias | Description | Default |
|--------|-------|-------------|---------|
| `--config` | `-c` | Path to configuration file | config.json |
| `--prompt` | `-p` | Path to prompt file | None |
| `--prd` | - | Path to PRD JSON file | None |
| `--api-url` | - | Override API URL | From config |
| `--output` | `-o` | Override output folder | From config |

## How It Works

OpenLlama follows a systematic approach to generate working code:

```
┌─────────────────────────────────────────────────────────────────┐
│                      OpenLlama Workflow                         │
├─────────────────────────────────────────────────────────────────┤
│  1. READ PROMPT                                                │
│     └─> Read prompt.txt describing desired software            │
│                                                                 │
│  2. GENERATE CODE                                              │
│     └─> Send prompt to llama.cpp server                        │
│     └─> Receive Python code in markdown blocks                 │
│                                                                 │
│  3. CREATE FILES                                                │
│     └─> Parse code blocks with filenames                       │
│     └─> Write files to output directory                        │
│                                                                 │
│  4. VALIDATE SYNTAX                                            │
│     └─> Check all Python files with py_compile                 │
│     └─> If errors → FIX & REPEAT (max 10 iterations)           │
│                                                                 │
│  5. RUN CODE                                                    │
│     └─> Execute main.py                                         │
│     └─> If runtime error → DEBUG & FIX (max 10 iterations)     │
│                                                                 │
│  6. RUN TESTS                                                  │
│     └─> Run pytest if tests exist                              │
│     └─> If tests fail → DEBUG & FIX (max 10 iterations)       │
│                                                                 │
│  7. COMPLETE                                                   │
│     └─> All checks passed → SUCCESS                            │
│     └─> Max iterations reached → FAIL                         │
└─────────────────────────────────────────────────────────────────┘
```

### Debug Loop

When errors are detected, OpenLlama:
1. Analyzes the error message
2. Sends the error + code context to LLM
3. Receives corrected code
4. Applies fixes
5. Re-runs validation
6. Repeats up to 10 times until resolved

## PRD Format

For PRD mode, use this JSON structure:

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
            "acceptanceCriteria": [
                "Criterion 1",
                "Criterion 2"
            ],
            "priority": 1,
            "passes": false,
            "notes": ""
        },
        {
            "id": "US-002",
            "title": "Another feature",
            "description": "More detail...",
            "acceptanceCriteria": ["Criterion A", "Criterion B"],
            "priority": 2,
            "passes": false,
            "notes": ""
        }
    ]
}
```

### PRD Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `project` | string | Yes | Project name |
| `branchName` | string | No | Git branch name |
| `description` | string | No | Project description |
| `userStories` | array | Yes | List of user stories |
| `id` | string | Yes | Unique story identifier |
| `title` | string | Yes | Story title |
| `description` | string | Yes | Story description |
| `acceptanceCriteria` | array | Yes | List of acceptance criteria |
| `priority` | number | Yes | Story priority (1 = highest) |
| `passes` | boolean | No | Completion status |
| `notes` | string | No | Additional notes |

## Examples

### Example 1: Simple Calculator

**prompt.txt**:
```
Create a simple calculator module with add, subtract, multiply, divide functions.
Include a main() function that demonstrates all operations with proper error handling.
```

**Run**:
```bash
python -m open_llama.main --prompt prompt.txt --output calculator/
```

### Example 2: API Client

**prompt.txt**:
```
Create a REST API client for a JSONPlaceholder API.
Include functions to:
- GET /posts
- GET /posts/{id}
- POST /posts
- GET /users
- GET /users/{id}
Use the requests library and handle errors gracefully.
```

### Example 3: Web Server

**prompt.txt**:
```
Create a simple Flask web server with:
- Home page showing "Welcome"
- /api/health endpoint returning JSON {"status": "ok"}
- /api/echo endpoint that echoes back POSTed JSON
Include proper error handling and logging.
```

### Example 4: With Custom Config

**config.json**:
```json
{
    "api_url": "http://192.168.1.100:5000/v1/chat/completions",
    "prmpt_path": "my_prompt.txt",
    "folder": "generated_code"
}
```

**Run**:
```bash
python -m open_llama.main --config config.json
```

### Example 5: PRD Workflow

**prd.json**:
```json
{
    "project": "Task Manager",
    "userStories": [
        {
            "id": "US-001",
            "title": "Add task",
            "description": "User can add a new task",
            "acceptanceCriteria": [
                "Task has title and description",
                "Task is saved to file",
                "Confirmation shown after save"
            ],
            "priority": 1
        },
        {
            "id": "US-002",
            "title": "List tasks",
            "description": "User can view all tasks",
            "acceptanceCriteria": [
                "All tasks displayed",
                "Shows task count"
            ],
            "priority": 2
        }
    ]
}
```

**Run**:
```bash
python -m open_llama.main --prd prd.json --output task_manager/
```

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success - all tasks completed |
| 1 | Failure - errors occurred |

## Troubleshooting

### Cannot connect to llama.cpp server

**Error**: `ConnectionError: Cannot connect to llama.cpp server`

**Solutions**:
1. Ensure llama.cpp server is running:
   ```bash
   ./server -m model.gguf -host 127.0.0.1 -port 5000
   ```

2. Check the URL matches your config:
   ```bash
   curl http://127.0.0.1:5000/v1/chat/completions
   ```

3. Verify firewall settings allow local connections

### No files created

**Problem**: OpenLlama runs but creates no files

**Solutions**:
1. Make sure your prompt is clear and specific
2. Include specific function/class names
3. Specify the desired output format

**Good prompt**:
```
Create a calculator.py file with add(a,b), subtract(a,b), 
multiply(a,b), divide(a,b) functions. Include type hints 
and handle divide by zero with ValueError.
```

**Bad prompt**:
```
Make a calculator
```

### Infinite loop in debugging

**Problem**: OpenLlama keeps trying to fix errors but never succeeds

**Solutions**:
1. Check the generated code manually in the output folder
2. Simplify your prompt
3. Break complex tasks into smaller prompts
4. OpenLlama limits debug iterations to 10 by default

### Tests timing out

**Problem**: Tests take too long to run

**Solutions**:
1. Increase timeout in `runner.py` (default: 120 seconds)
2. Simplify the generated test cases
3. Add `@pytest.mark.timeout` decorators to tests

### Out of memory

**Problem**: llama.cpp server runs out of memory

**Solutions**:
1. Use a smaller model
2. Reduce context size: `-c 2048`
3. Add swap space
4. Close other applications

## Best Practices

### Writing Good Prompts

1. **Be Specific**: Include exact function names, parameters, return types
2. **Define Structure**: Specify file organization
3. **Include Error Handling**: Ask for proper error handling
4. **Add Examples**: Show expected input/output

### Project Organization

```
my_project/
├── prompt.txt           # Your prompt
├── config.json          # Configuration
├── prd.json             # PRD (for PRD mode)
├── generated/           # Generated code (auto-created)
└── open_llama_db.json   # Database (auto-created)
```

### Iterative Development

1. Start with simple prompts
2. Test the output
3. Refine your prompt based on results
4. Gradually add complexity

## Security Considerations

- OpenLlama runs locally - no data leaves your machine
- Generated code should be reviewed before execution
- Be cautious with `exec()` or similar code execution
- Validate any external inputs in generated code

## Getting Help

- Check [README.md](README.md) for overview
- See [MAINTENANCE.md](MAINTENANCE.md) for developer docs
- Review test files for usage examples
