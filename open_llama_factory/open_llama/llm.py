"""LLM client for llama.cpp server."""

import json
import requests
from typing import Optional


class LLMClient:
    def __init__(self, api_url: str, model: str = "local-model"):
        self.api_url = api_url
        self.model = model
        self.session = requests.Session()

    def chat(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 4096) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": False
        }

        try:
            response = self.session.post(self.api_url, json=payload, timeout=300)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Cannot connect to llama.cpp server at {self.api_url}")
        except KeyError as e:
            raise ValueError(f"Unexpected response format: {e}")
        except Exception as e:
            raise RuntimeError(f"LLM request failed: {e}")

    def generate_code(self, task: str, context: Optional[str] = None) -> str:
        system_prompt = """You are an expert Python developer. Generate clean, well-structured code.
Rules:
1. Create complete, working Python files
2. Use type hints for all functions
3. Follow PEP 8 style guidelines
4. Include docstrings for modules and functions
5. Create __init__.py files for packages
6. Handle errors gracefully"""
        
        user_prompt = f"Task: {task}\n\n"
        if context:
            user_prompt += f"Context:\n{context}\n\n"
        user_prompt += "Generate the complete code implementation."

        return self.chat(user_prompt, system_prompt)
