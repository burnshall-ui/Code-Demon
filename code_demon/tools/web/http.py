"""
HTTP Request Tools

Fetch URLs and make HTTP requests
"""

import aiohttp
from typing import Dict, Any
from ..registry import Tool, ToolMetadata, ToolCategory, ToolParameter


class FetchURLTool(Tool):
    """Tool to fetch URL content"""

    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="fetch_url",
            description="Fetch content from a URL. Returns the response body.",
            category=ToolCategory.WEB,
            parameters=[
                ToolParameter(
                    name="url",
                    type="string",
                    description="URL to fetch",
                    required=True,
                ),
                ToolParameter(
                    name="method",
                    type="string",
                    description="HTTP method (GET, POST, etc.)",
                    required=False,
                    default="GET",
                    enum=["GET", "POST", "PUT", "DELETE", "PATCH"],
                ),
                ToolParameter(
                    name="headers",
                    type="object",
                    description="HTTP headers as JSON object",
                    required=False,
                    default=None,
                ),
            ],
            requires_approval=False,
            dangerous=False,
            timeout=30,
        )

    async def execute(
        self, url: str, method: str = "GET", headers: Dict[str, str] | None = None
    ) -> str:
        """Fetch URL content"""
        try:
            if not url.startswith(("http://", "https://")):
                return f"Error: Invalid URL '{url}'. Must start with http:// or https://"

            # Set default headers
            default_headers = {
                "User-Agent": "CodeDemon/1.0",
            }
            if headers:
                default_headers.update(headers)

            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method, url, headers=default_headers, timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    # Get response text
                    text = await response.text()

                    # Build output
                    output = []
                    output.append(f"🌐 URL: {url}")
                    output.append(f"📊 Status: {response.status} {response.reason}")
                    output.append(f"📏 Content-Type: {response.content_type}")
                    output.append(f"📦 Size: {len(text)} bytes")
                    output.append("")
                    output.append("📄 Content:")
                    output.append("")

                    # Truncate if too long
                    if len(text) > 10000:
                        text = text[:10000] + "\n\n... (truncated, content too long)"

                    output.append(text)

                    return "\n".join(output)

        except aiohttp.ClientError as e:
            return f"Error fetching URL: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"


class CallAPITool(Tool):
    """Tool to call REST APIs"""

    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="call_api",
            description="Make a REST API call with JSON payload. Returns the JSON response.",
            category=ToolCategory.WEB,
            parameters=[
                ToolParameter(
                    name="url",
                    type="string",
                    description="API endpoint URL",
                    required=True,
                ),
                ToolParameter(
                    name="method",
                    type="string",
                    description="HTTP method",
                    required=False,
                    default="GET",
                    enum=["GET", "POST", "PUT", "DELETE", "PATCH"],
                ),
                ToolParameter(
                    name="data",
                    type="object",
                    description="JSON data to send (for POST/PUT/PATCH)",
                    required=False,
                    default=None,
                ),
                ToolParameter(
                    name="headers",
                    type="object",
                    description="HTTP headers",
                    required=False,
                    default=None,
                ),
            ],
            requires_approval=False,
            dangerous=False,
            timeout=30,
        )

    async def execute(
        self,
        url: str,
        method: str = "GET",
        data: Dict[str, Any] | None = None,
        headers: Dict[str, str] | None = None,
    ) -> str:
        """Call REST API"""
        try:
            if not url.startswith(("http://", "https://")):
                return f"Error: Invalid URL '{url}'"

            # Set default headers
            default_headers = {
                "User-Agent": "CodeDemon/1.0",
                "Content-Type": "application/json",
            }
            if headers:
                default_headers.update(headers)

            async with aiohttp.ClientSession() as session:
                kwargs = {"headers": default_headers, "timeout": aiohttp.ClientTimeout(total=30)}

                if data and method in ["POST", "PUT", "PATCH"]:
                    kwargs["json"] = data

                async with session.request(method, url, **kwargs) as response:
                    # Try to parse as JSON
                    try:
                        json_data = await response.json()
                        import json

                        json_str = json.dumps(json_data, indent=2)
                    except Exception:
                        # Fallback to text
                        json_str = await response.text()

                    # Build output
                    output = []
                    output.append(f"🌐 API: {url}")
                    output.append(f"📊 Status: {response.status} {response.reason}")
                    output.append("")
                    output.append("📦 Response:")
                    output.append("")

                    # Truncate if too long
                    if len(json_str) > 5000:
                        json_str = json_str[:5000] + "\n\n... (truncated)"

                    output.append(json_str)

                    return "\n".join(output)

        except aiohttp.ClientError as e:
            return f"Error calling API: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"


class WebSearchTool(Tool):
    """Tool to search the web (simplified - just a placeholder)"""

    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="web_search",
            description="Search the web for information (placeholder - requires API key configuration)",
            category=ToolCategory.WEB,
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="Search query",
                    required=True,
                ),
                ToolParameter(
                    name="limit",
                    type="number",
                    description="Number of results to return",
                    required=False,
                    default=5,
                ),
            ],
            requires_approval=False,
            dangerous=False,
            timeout=30,
        )

    async def execute(self, query: str, limit: int = 5) -> str:
        """
        Web search (placeholder)
        
        Note: This is a placeholder. To enable real web search, you need to:
        1. Get an API key from a search provider (e.g., SerpAPI, Bing, Google)
        2. Implement the actual search logic
        """
        return f"""🔍 Web Search (Placeholder)

Query: {query}
Limit: {limit} results

⚠ This is a placeholder tool. To enable web search:

1. Get an API key from a search provider:
   - SerpAPI (https://serpapi.com)
   - Bing Search API (https://www.microsoft.com/en-us/bing/apis/bing-web-search-api)
   - Google Custom Search (https://developers.google.com/custom-search)

2. Add the API key to your .env file:
   SEARCH_API_KEY=your_key_here
   SEARCH_PROVIDER=serpapi

3. Implement the search logic in this tool

For now, try using fetch_url to directly access websites or call_api for REST APIs.
"""

