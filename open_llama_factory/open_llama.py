#!/usr/bin/env python3
"""
OpenLLaMA - Autonomous AI coding agent using local llama.cpp server

Usage:
    python3 open_llama.py -p <prompt_file> -f <output_folder>
    python3 open_llama.py --prompt <prompt_file> --folder <output_folder>
    python3 open_llama.py -h | --help
"""

import argparse
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

DEFAULT_API_URL = "http://192.168.1.176:5000/v1/chat/completions"


def parse_args():
    parser = argparse.ArgumentParser(
        description="OpenLLaMA - Autonomous AI coding agent using local llama.cpp server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 open_llama.py -p prompt.txt -f output/
  python3 open_llama.py --prompt prompt.txt --folder output/
  python3 open_llama.py -c config.json
        """
    )
    parser.add_argument(
        "-p", "--prompt",
        help="Path to prompt file describing the software to generate"
    )
    parser.add_argument(
        "-f", "--folder", "--output",
        dest="folder",
        help="Output directory for generated files"
    )
    parser.add_argument(
        "-c", "--config",
        default="config.json",
        help="Path to configuration file (default: config.json)"
    )
    parser.add_argument(
        "-a", "--api-url",
        default=DEFAULT_API_URL,
        help=f"LLM API URL (default: {DEFAULT_API_URL})"
    )
    parser.add_argument(
        "--prd",
        help="Path to PRD JSON file for PRD mode"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    return parser.parse_args()


def load_config(config_path: str) -> dict:
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        return {}


def main():
    args = parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    config = {}
    
    if Path(args.config).exists():
        config = load_config(args.config)
        logger.info(f"Loaded config from {args.config}")
    
    prompt_file = args.prompt or config.get("prmpt_path") or config.get("prompt_path")
    output_folder = args.folder or config.get("folder") or config.get("output")
    api_url = args.api_url or config.get("api_url") or DEFAULT_API_URL
    
    if args.prd:
        logger.info("PRD mode requested")
        logger.error("PRD mode not yet implemented in single-file mode")
        sys.exit(1)
    
    if not prompt_file:
        logger.error("No prompt file specified. Use -p or --prompt")
        sys.exit(1)
    
    prompt_path = Path(prompt_file)
    if not prompt_path.exists():
        logger.error(f"Prompt file not found: {prompt_file}")
        sys.exit(1)
    
    if not output_folder:
        logger.error("No output folder specified. Use -f or --folder")
        sys.exit(1)
    
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Reading prompt from: {prompt_path}")
    with open(prompt_path, "r") as f:
        prompt_content = f.read()
    
    logger.info(f"Using LLM API: {api_url}")
    logger.info(f"Output folder: {output_path}")
    
    try:
        import requests
        
        system_prompt = """You are an expert Python developer. Generate complete Python code files.

CRITICAL RULES:
1. Your response must ONLY contain code in properly formatted markdown blocks
2. Do NOT include explanations, comments like "filename:", or placeholder text
3. The main() function MUST handle any exceptions gracefully (use try/except)
4. If a function raises ValueError, the main() must catch and display it
5. Write ONLY the actual Python code, nothing else

Example format:

```python
def add(a: float, b: float) -> float:
    return a + b

def main():
    print("Result:", add(5, 3))

if __name__ == "__main__":
    main()
```
"""
        
        user_prompt = f"""Create Python code for the following requirement:

{prompt_content}

Return the code in a single markdown code block."""
        
        logger.info("Generating code from LLM...")
        
        payload = {
            "model": "local-model",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 4096,
            "stream": False
        }
        
        response = requests.post(api_url, json=payload, timeout=300)
        response.raise_for_status()
        data = response.json()
        generated_code = data["choices"][0]["message"]["content"]
        
        logger.info("Parsing generated code...")
        
        import re
        blocks = []
        lines = generated_code.split('\n')
        current_code = []
        in_block = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('```') and not in_block:
                in_block = True
                current_code = []
                continue
            if stripped.startswith('```') and in_block:
                in_block = False
                code = '\n'.join(current_code).strip()
                if code:
                    blocks.append(code)
                continue
            if in_block:
                current_code.append(line)
        
        if not blocks:
            logger.error("No code blocks found in LLM response")
            sys.exit(1)
        
        main_code = blocks[0]
        
        main_file = output_path / "main.py"
        
        if 'def main(' in main_code:
            pass
        elif 'if __name__' in main_code:
            pass
        else:
            main_code += "\n\nif __name__ == '__main__':\n    main()"
        
        logger.info(f"Writing code to: {main_file}")
        with open(main_file, "w") as f:
            f.write(main_code)
        
        logger.info("Checking syntax...")
        import py_compile
        py_compile.compile(str(main_file), doraise=True)
        
        logger.info("Running generated code...")
        import subprocess
        result = subprocess.run(
            [sys.executable, str(main_file)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            logger.info("SUCCESS! Generated code executed successfully:")
            print("\n" + "="*60)
            print(result.stdout)
            print("="*60)
        else:
            logger.warning("Code executed with errors:")
            print("\n" + "="*60)
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            print("="*60)
        
        logger.info(f"Generated files in: {output_path}")
        logger.info("Done!")
        
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.info("Install required packages: pip install requests")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to LLM server at {api_url}")
        logger.info("Make sure your llama.cpp server is running")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
