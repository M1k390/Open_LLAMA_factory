"""Main Ralph orchestrator."""

import sys
import logging
from pathlib import Path
from typing import Optional

from config import OpenLlamaConfig
from llm import LLMClient
from generator import CodeGenerator
from runner import Runner
from debugger import Debugger
from store import ProgressDB, PRDStore


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class OpenLlama:
    def __init__(self, config: RalphConfig):
        self.config = config
        self.output_dir = config.ensure_output_dir()
        self.llm = LLMClient(config.api_url)
        self.generator = CodeGenerator(self.llm, self.output_dir)
        self.runner = Runner(self.output_dir)
        self.debugger = Debugger(self.llm, self.runner, self.output_dir)
        
        db_path = self.output_dir / "open_llama_db.json"
        self.db = ProgressDB(db_path)
        self.prd_store = PRDStore(self.db)

    def run_prompt_mode(self, prompt_file: str):
        """Read prompt from file, generate software, test and debug until working."""
        prompt_path = Path(prompt_file)
        if not prompt_path.exists():
            logger.error(f"Prompt file not found: {prompt_file}")
            return False

        with open(prompt_path, "r") as f:
            prompt_content = f.read()

        logger.info("Generating code from prompt...")
        generated_code = self.generator.generate_from_prompt(prompt_content)
        
        logger.info("Creating files from generated code...")
        created_files = self.generator.create_files(generated_code)
        
        if not created_files:
            logger.error("No files were created")
            return False

        logger.info(f"Created {len(created_files)} files")
        for f in created_files:
            logger.info(f"  - {f}")

        return self.test_and_debug_loop(created_files)

    def test_and_debug_loop(self, files: list, max_iterations: int = 10) -> bool:
        """Run tests and debug loop until code works or max iterations reached."""
        for iteration in range(1, max_iterations + 1):
            logger.info(f"\n=== Test Iteration {iteration} ===")

            syntax_ok, syntax_errors = self.runner.check_all_syntax()
            if not syntax_ok:
                logger.warning(f"Syntax errors found: {len(syntax_errors)}")
                for error in syntax_errors:
                    logger.warning(f"  {error}")
                
                if iteration < max_iterations:
                    logger.info("Attempting to fix syntax errors...")
                    fixed, response = self.debugger.handle_syntax_errors(syntax_errors)
                    if fixed:
                        files = self.generator.create_files(response)
                        continue
                    else:
                        logger.error(f"Could not fix: {response}")
                        return False
                else:
                    return False

            main_file = self.output_dir / "main.py"
            if not main_file.exists():
                py_files = list(self.output_dir.glob("*.py"))
                if py_files:
                    main_file = py_files[0]
            
            if main_file.exists():
                logger.info(f"Running {main_file.name}...")
                result = self.runner.run_python_file(main_file)
                if result.success:
                    logger.info("Execution successful!")
                    logger.info(f"Output:\n{result.output}")
                else:
                    logger.warning(f"Execution failed:\n{result.error}")
                    
                    if iteration < max_iterations:
                        logger.info("Attempting to fix runtime error...")
                        fixed, response = self.debugger.handle_runtime_error(
                            result.error or "Unknown error",
                            main_file
                        )
                        if fixed:
                            files = self.generator.create_files(response)
                            continue
                    return False

            logger.info("Checking for tests...")
            test_result = self.runner.run_tests()
            if test_result.success or "no tests" in test_result.output.lower():
                logger.info("All checks passed!")
                return True
            else:
                logger.warning("Tests failed")
                if iteration < max_iterations:
                    fixed, response = self.debugger.handle_test_failure(test_result.output)
                    if fixed:
                        files = self.generator.create_files(response)
                        continue
                return False

        logger.warning("Max iterations reached")
        return False

    def run_prd_mode(self, prd_file: str) -> bool:
        """Run in PRD mode: process user stories from prd.json."""
        prd_path = Path(prd_file)
        if not prd_path.exists():
            logger.error(f"PRD file not found: {prd_file}")
            return False

        with open(prd_path, "r") as f:
            prd_data = f.read()
        
        import json
        prd = json.loads(prd_data)
        self.prd_store.save_prd(prd)

        story = self.prd_store.get_next_story()
        while story:
            logger.info(f"\n=== Working on: {story['id']} - {story['title']} ===")
            
            prompt = f"""
User Story: {story['title']}
Description: {story['description']}
Acceptance Criteria:
{chr(10).join(f'- {c}' for c in story.get('acceptanceCriteria', []))}
"""
            
            generated_code = self.generator.generate_from_prompt(prompt)
            created_files = self.generator.create_files(generated_code)
            
            success = self.test_and_debug_loop(created_files)
            self.prd_store.update_story_status(story["id"], success)
            
            self.db.add_progress(
                story["id"],
                story["title"],
                [str(f) for f in created_files],
                []
            )
            
            if success:
                logger.info(f"Story {story['id']} completed!")
            else:
                logger.error(f"Story {story['id']} failed")
            
            story = self.prd_store.get_next_story()

        logger.info("All stories completed!")
        return True

    def close(self):
        """Close database connections."""
        self.db.close()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenLlama - Autonomous coding agent")
    parser.add_argument("--config", "-c", default="config.json", help="Configuration file path")
    parser.add_argument("--prompt", "-p", help="Prompt file to process")
    parser.add_argument("--prd", help="PRD JSON file to process")
    parser.add_argument("--api-url", help="Override API URL")
    parser.add_argument("--output", "-o", help="Override output folder")
    
    args = parser.parse_args()

    config_path = Path(args.config)
    if config_path.exists():
        config = OpenLlamaConfig.from_file(str(config_path))
    else:
        config = OpenLlamaConfig(
            api_url=args.api_url or "http://192.168.1.176:5000/v1/chat/completions",
            prmpt_path=args.prompt or "prompt.txt",
            folder=args.output or "output"
        )

    open_llama = OpenLlama(config)
    
    try:
        if args.prd:
            success = open_llama.run_prd_mode(args.prd)
        elif args.prompt:
            success = open_llama.run_prompt_mode(args.prompt)
        else:
            logger.error("Please specify --prompt or --prd")
            sys.exit(1)
        
        sys.exit(0 if success else 1)
    finally:
        open_llama.close()


if __name__ == "__main__":
    main()
