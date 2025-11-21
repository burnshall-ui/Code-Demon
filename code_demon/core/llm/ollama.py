"""
Ollama LLM Provider

Integration with Ollama API for local LLM inference
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


class OllamaProvider(LLMProvider):
    """Ollama LLM provider implementation"""

    def __init__(self, model: str, base_url: str = "http://localhost:11434"):
        super().__init__(model, base_url)
        self.timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes

    def _convert_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert Message objects to Ollama format"""
        ollama_messages = []
        for msg in messages:
            ollama_msg: Dict[str, Any] = {
                "role": msg.role.value,
                "content": msg.content,
            }
            if msg.tool_calls:
                ollama_msg["tool_calls"] = msg.tool_calls
            ollama_messages.append(ollama_msg)
        return ollama_messages

    def _convert_tools(self, tools: List[ToolDefinition]) -> List[Dict[str, Any]]:
        """Convert ToolDefinition objects to Ollama format"""
        ollama_tools = []
        for tool in tools:
            ollama_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    },
                }
            )
        return ollama_tools

    def _parse_tool_calls(self, response_data: Dict[str, Any]) -> List[ToolCall]:
        """Parse tool calls from Ollama response"""
        tool_calls = []
        message = response_data.get("message", {})
        raw_tool_calls = message.get("tool_calls", [])

        for idx, tc in enumerate(raw_tool_calls):
            func = tc.get("function", {})
            tool_calls.append(
                ToolCall(
                    id=tc.get("id", f"call_{idx}"),
                    name=func.get("name", ""),
                    arguments=func.get("arguments", {}),
                )
            )
        return tool_calls

    async def chat(
        self,
        messages: List[Message],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Send chat request to Ollama"""
        url = f"{self.base_url}/api/chat"

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": self._convert_messages(messages),
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        if tools:
            payload["tools"] = self._convert_tools(tools)

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise LLMConnectionError(
                            f"Ollama API error: {response.status} - {text}"
                        )

                    data = await response.json()

                    # Extract response content
                    message = data.get("message", {})
                    content = message.get("content", "")

                    # Parse tool calls if present
                    tool_calls = self._parse_tool_calls(data)

                    # Calculate performance metrics
                    eval_count = data.get("eval_count", 0)
                    eval_duration = data.get("eval_duration", 0)
                    tokens_per_sec = None
                    if eval_count and eval_duration:
                        # eval_duration is in nanoseconds
                        tokens_per_sec = eval_count / (eval_duration / 1e9)

                    return LLMResponse(
                        content=content,
                        tool_calls=tool_calls,
                        finish_reason=data.get("done_reason", "stop"),
                        model=self.model,
                        tokens_used=eval_count,
                        tokens_per_second=tokens_per_sec,
                    )

        except aiohttp.ClientError as e:
            raise LLMConnectionError(f"Failed to connect to Ollama: {e}")
        except asyncio.TimeoutError:
            raise LLMTimeoutError("Ollama request timed out")

    async def stream_chat(
        self,
        messages: List[Message],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream chat response from Ollama"""
        url = f"{self.base_url}/api/chat"

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": self._convert_messages(messages),
            "stream": True,
            "options": {
                "temperature": temperature,
            },
        }

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        if tools:
            payload["tools"] = self._convert_tools(tools)

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise LLMConnectionError(
                            f"Ollama API error: {response.status} - {text}"
                        )

                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line)
                                message = data.get("message", {})
                                content = message.get("content", "")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue

        except aiohttp.ClientError as e:
            raise LLMConnectionError(f"Failed to connect to Ollama: {e}")

    def supports_tools(self) -> bool:
        """Ollama supports tool calling"""
        return True

    async def health_check(self) -> bool:
        """Check if Ollama is available"""
        url = f"{self.base_url}/api/tags"
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=5)
            ) as session:
                async with session.get(url) as response:
                    return response.status == 200
        except Exception:
            return False
