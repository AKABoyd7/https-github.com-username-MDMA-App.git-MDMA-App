"""
Tests for Local Models integration (LM Studio).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from mcp_server.tools import local_models


class TestLMStudioClient:
    """Test LM Studio client functionality."""

    @patch('mcp_server.tools.local_models.requests.get')
    def test_is_connected_success(self, mock_get):
        """Test successful connection check."""
        mock_get.return_value = Mock(status_code=200)

        client = local_models.LMStudioClient()
        assert client.is_connected() is True

    @patch('mcp_server.tools.local_models.requests.get')
    def test_is_connected_failure(self, mock_get):
        """Test failed connection check."""
        mock_get.side_effect = Exception("Connection refused")

        client = local_models.LMStudioClient()
        assert client.is_connected() is False


class TestChatTools:
    """Test chat tool functions."""

    @patch('mcp_server.tools.local_models.get_lm_client')
    def test_chat_llama33_basic(self, mock_client):
        """Test basic Llama 3.3 chat."""
        mock_lm = MagicMock()
        mock_lm.chat_completion.return_value = {
            "response": "Test response",
            "model": "llama-3.3-70b-instruct",
            "tokens_used": 100,
            "execution_time": 2.5
        }
        mock_client.return_value = mock_lm

        result = local_models.chat_llama33(
            prompt="Test prompt",
            temperature=0.7
        )

        assert result["response"] == "Test response"
        assert result["model"] == "llama-3.3-70b-instruct"
        assert "execution_time" in result

    @patch('mcp_server.tools.local_models.get_lm_client')
    def test_chat_qwen_with_system_prompt(self, mock_client):
        """Test Qwen chat with system prompt."""
        mock_lm = MagicMock()
        mock_lm.chat_completion.return_value = {
            "response": "Code example",
            "model": "qwen2.5-coder-32b-instruct",
            "tokens_used": 150,
            "execution_time": 3.0
        }
        mock_client.return_value = mock_lm

        result = local_models.chat_qwen(
            prompt="Write a Python function",
            temperature=0.5
        )

        # Should have default system prompt for coding
        mock_lm.chat_completion.assert_called_once()
        call_args = mock_lm.chat_completion.call_args
        assert "system_prompt" in call_args[1] or len(call_args[0]) > 0


class TestModelManagement:
    """Test model management tools."""

    @patch('mcp_server.tools.local_models.get_lm_client')
    def test_list_local_models_connected(self, mock_client):
        """Test listing models when connected."""
        mock_lm = MagicMock()
        mock_lm.is_connected.return_value = True
        mock_lm.list_models.return_value = [
            {"model_name": "llama-3.3-70b-instruct", "status": "available"},
            {"model_name": "qwen2.5-coder-32b-instruct", "status": "available"}
        ]
        mock_client.return_value = mock_lm

        result = local_models.list_local_models()

        assert result["success"] is True
        assert len(result["models"]) >= 2
        assert result["lm_studio_connected"] is True

    @patch('mcp_server.tools.local_models.get_lm_client')
    def test_list_local_models_disconnected(self, mock_client):
        """Test listing models when disconnected."""
        mock_lm = MagicMock()
        mock_lm.is_connected.return_value = False
        mock_client.return_value = mock_lm

        result = local_models.list_local_models()

        assert result["success"] is False
        assert "error" in result

    @patch('mcp_server.tools.local_models.get_lm_client')
    def test_load_model_success(self, mock_client):
        """Test successful model loading."""
        mock_lm = MagicMock()
        mock_lm.is_connected.return_value = True
        mock_lm.chat_completion.return_value = {
            "response": "Test",
            "execution_time": 1.0
        }
        mock_client.return_value = mock_lm

        result = local_models.load_model("llama-3.3-70b-instruct")

        assert result["success"] is True
        assert result["model_name"] == "llama-3.3-70b-instruct"
        assert "load_time" in result

    def test_load_model_invalid_name(self):
        """Test loading invalid model name."""
        result = local_models.load_model("invalid-model-name")

        assert result["success"] is False
        assert "Unknown model" in result["message"]


class TestToolRegistration:
    """Test tool registration."""

    def test_get_tools_returns_list(self):
        """Test that get_tools returns a list."""
        tools = local_models.get_tools()

        assert isinstance(tools, list)
        assert len(tools) == 7  # Should have 7 local model tools

    def test_tool_definitions_complete(self):
        """Test that all tool definitions are complete."""
        tools = local_models.get_tools()

        required_keys = ["name", "description", "inputSchema", "handler"]

        for tool in tools:
            for key in required_keys:
                assert key in tool, f"Tool missing {key}: {tool.get('name', 'unknown')}"

            # Check that handler is callable
            assert callable(tool["handler"])

            # Check that inputSchema has required structure
            assert "type" in tool["inputSchema"]
            assert "properties" in tool["inputSchema"]


@pytest.mark.integration
class TestLMStudioIntegration:
    """Integration tests requiring actual LM Studio connection."""

    @pytest.mark.skip(reason="Requires LM Studio running")
    def test_actual_chat_llama33(self):
        """Test actual chat with Llama 3.3 (requires LM Studio)."""
        result = local_models.chat_llama33(
            prompt="What is 2+2?",
            max_tokens=50
        )

        assert "response" in result
        assert result["model"] == "llama-3.3-70b-instruct"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
