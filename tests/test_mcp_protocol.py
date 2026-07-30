import sys
import unittest
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


ROOT = Path(__file__).resolve().parents[1]


class MCPProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def test_server_initializes_and_lists_tools(self):
        params = StdioServerParameters(command=sys.executable, args=["-m", "mcp_server.server"], cwd=ROOT)
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.list_tools()
        self.assertEqual({tool.name for tool in result.tools}, {"stack_health", "list_local_models", "generate_local", "rerank_documents"})


if __name__ == "__main__":
    unittest.main()
