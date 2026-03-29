"""Tests for LLM client module."""

import pytest
from unittest.mock import Mock, patch
from llm import LLMClient


class TestLLMClient:
    def test_init(self):
        client = LLMClient("http://test:8080/v1/chat")
        assert client.api_url == "http://test:8080/v1/chat"
        assert client.model == "local-model"

    def test_init_custom_model(self):
        client = LLMClient("http://test:8080", model="custom-model")
        assert client.model == "custom-model"

    @patch('llm.requests.Session')
    def test_chat_success(self, mock_session_class):
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_session.post.return_value = mock_response
        
        client = LLMClient("http://test:8080")
        result = client.chat("Hello")
        
        assert result == "Test response"
        mock_session.post.assert_called_once()

    @patch('llm.requests.Session')
    def test_chat_with_system_prompt(self, mock_session_class):
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Response"}}]
        }
        mock_session.post.return_value = mock_response
        
        client = LLMClient("http://test:8080")
        client.chat("User message", system_prompt="You are helpful")
        
        call_args = mock_session.post.call_args
        payload = call_args[1]['json']
        assert len(payload['messages']) == 2
        assert payload['messages'][0]['role'] == 'system'
        assert payload['messages'][1]['role'] == 'user'

    @patch('llm.requests.Session')
    def test_chat_connection_error(self, mock_session_class):
        import requests
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.post.side_effect = requests.exceptions.ConnectionError()
        
        client = LLMClient("http://test:8080")
        
        with pytest.raises(ConnectionError) as exc_info:
            client.chat("Hello")
        assert "Cannot connect" in str(exc_info.value)

    @patch('llm.requests.Session')
    def test_generate_code(self, mock_session_class):
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "def hello(): pass"}}]
        }
        mock_session.post.return_value = mock_response
        
        client = LLMClient("http://test:8080")
        result = client.generate_code("Create a hello function")
        
        assert "def hello" in result
