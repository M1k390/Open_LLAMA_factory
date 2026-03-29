"""Tests for config module."""

import json
import tempfile
from pathlib import Path
from config import OpenLlamaConfig


class TestOpenLlamaConfig:
    def test_from_dict_defaults(self):
        config = OpenLlamaConfig.from_dict({})
        assert config.api_url == "http://192.168.1.176:5000/v1/chat/completions"
        assert config.prmpt_path == "prompt.txt"
        assert config.folder == "output"

    def test_from_dict_custom(self):
        config = OpenLlamaConfig.from_dict({
            "api_url": "http://localhost:8080/v1/chat",
            "prmpt_path": "my_prompt.txt",
            "folder": "my_output"
        })
        assert config.api_url == "http://localhost:8080/v1/chat"
        assert config.prmpt_path == "my_prompt.txt"
        assert config.folder == "my_output"

    def test_from_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "api_url": "http://test:1234/v1",
                "prmpt_path": "test_prompt.txt",
                "folder": "test_folder"
            }, f)
            f.flush()
            
            config = OpenLlamaConfig.from_file(f.name)
            
            assert config.api_url == "http://test:1234/v1"
            assert config.prmpt_path == "test_prompt.txt"
            assert config.folder == "test_folder"
            
            Path(f.name).unlink()

    def test_ensure_output_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = OpenLlamaConfig(
                api_url="http://test:8080",
                prmpt_path="prompt.txt",
                folder=tmpdir + "/new_dir/subdir"
            )
            result = config.ensure_output_dir()
            
            assert result.exists()
            assert result.is_dir()

    def test_get_prompt_content(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test prompt content")
            f.flush()
            
            config = OpenLlamaConfig(
                api_url="http://test:8080",
                prmpt_path=f.name,
                folder="output"
            )
            
            content = config.get_prompt_content()
            assert content == "Test prompt content"
            
            Path(f.name).unlink()
