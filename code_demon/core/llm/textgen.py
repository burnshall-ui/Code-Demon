"""
Text Generation WebUI Provider

Integration with Text Generation WebUI (oobabooga) API
"""

import json
import aiohttp
from typing import List, Optional, AsyncGenerator, Dict, Any
from .base import (
    LLMProvider,
    Message,
    ToolDefinition,
    ToolCall,
    LLMResponse,
    LLMConnectionError,
    LLMTimeoutError,
    MessageRole,
)


class TextGenProvider(LLMProvider):
    """Text Generation WebUI provider implementation"""

    def __init__(self, model: str = "default", base_url: str = "http://localhost:5000"):
        super().__init__(model, base_url)
        self.timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes

    def _convert_messages_to_prompt(self, messages: List[Message]) -> str:
        """
        Convert messages to a single prompt string
        TextGen doesn't support conversation format natively
        """
        prompt_parts = []
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                prompt_parts.append(f"System: {msg.content}")
            elif msg.role == MessageRole.USER:
                prompt_parts.append(f"User: {msg.content}")
            elif msg.role == MessageRole.ASSISTANT:
                prompt_parts.append(f"Assistant: {msg.content}")
            elif msg.role == MessageRole.TOOL:
                prompt_parts.append(f"Tool Result: {msg.content}")

        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)

    async def chat(
        self,
        messages: List[Message],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Send chat request to Text Generation WebUI"""
        url = f"{self.base_url}/api/v1/generate"

        prompt = self._convert_messages_to_prompt(messages)

        # Add tool descriptions to prompt if provided
        if tools:
            tool_descriptions = "\n\nAvailable Tools:\n"
            for tool in tools:
                tool_descriptions += f"- {tool.name}: {tool.description}\n"
            # Insert before the last "Assistant:" line
            parts = prompt.rsplit("Assistant:", 1)
            prompt = parts[0] + tool_descriptions + "\nAssistant:" + parts[1]

        payload: Dict[str, Any] = {
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens or 500,
            "stop": ["User:", "System:"],
        }

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise LLMConnectionError(
                            f"TextGen API error: {response.status} - {text}"
                        )

                    data = await response.json()
                    content = data.get("results", [{}])[0].get("text", "").strip()

                    # TextGen doesn't support native tool calling
                    # We return empty tool_calls
                    return LLMResponse(
                        content=content,
                        tool_calls=[],
                        finish_reason="stop",
                        model=self.model,
                        tokens_used=None,
                        tokens_per_second=None,
                    )

        except aiohttp.ClientError as e:
            raise LLMConnectionError(f"Failed to connect to TextGen: {e}")
        except asyncio.TimeoutError:
            raise LLMTimeoutError("TextGen request timed out")

    async def stream_chat(
        self,
        messages: List[Message],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream chat response from Text Generation WebUI"""
        url = f"{self.base_url}/api/v1/stream"

        prompt = self._convert_messages_to_prompt(messages)

        if tools:
            tool_descriptions = "\n\nAvailable Tools:\n"
            for tool in tools:
                tool_descriptions += f"- {tool.name}: {tool.description}\n"
            parts = prompt.rsplit("Assistant:", 1)
            prompt = parts[0] + tool_descriptions + "\nAssistant:" + parts[1]

        payload: Dict[str, Any] = {
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens or 500,
            "stop": ["User:", "System:"],
        }

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise LLMConnectionError(
                            f"TextGen API error: {response.status} - {text}"
                        )

                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line)
                                token = data.get("token", "")
                                if token:
                                    yield token
                            except json.JSONDecodeError:
                                continue

        except aiohttp.ClientError as e:
            raise LLMConnectionError(f"Failed to connect to TextGen: {e}")

    def supports_tools(self) -> bool:
        """TextGen doesn't support native tool calling"""
        return False

    async def health_check(self) -> bool:
        """Check if TextGen is available"""
        url = f"{self.base_url}/api/v1/model"
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=5)
            ) as session:
                async with session.get(url) as response:
                    return response.status == 200
        except Exception:
            return False


# For convenience
import asyncio

