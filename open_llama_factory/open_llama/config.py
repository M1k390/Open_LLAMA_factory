"""Configuration management for OpenLlama."""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class OpenLlamaConfig:
    api_url: str
    prmpt_path: str
    folder: str

    @classmethod
    def from_file(cls, path: str) -> "OpenLlamaConfig":
        with open(path, "r") as f:
            data = json.load(f)
        return cls(
            api_url=data["api_url"],
            prmpt_path=data["prmpt_path"],
            folder=data["folder"]
        )

    @classmethod
    def from_dict(cls, data: dict) -> "OpenLlamaConfig":
        return cls(
            api_url=data.get("api_url", "http://192.168.1.176:5000/v1/chat/completions"),
            prmpt_path=data.get("prmpt_path", "prompt.txt"),
            folder=data.get("folder", "output")
        )

    def ensure_output_dir(self) -> Path:
        path = Path(self.folder)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_prompt_content(self) -> str:
        with open(self.prmpt_path, "r") as f:
            return f.read()
