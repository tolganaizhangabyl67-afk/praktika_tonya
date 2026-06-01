import logging
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)

ALLOWED_DIR = "C:/Users/ПК/Desktop/practika"


async def list_files_via_mcp(path: str = ".") -> str:
    try:
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", ALLOWED_DIR]
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                logger.info(f"Tools: {[t.name for t in tools.tools]}")
                result = await session.call_tool(
                    "list_directory",
                    arguments={"path": ALLOWED_DIR}
                )
                text = ""
                for item in result.content:
                    text += item.text + "\n"
                return "📁 Файлдар:\n\n" + text
    except Exception as e:
        logger.error(f"MCP қате: {e}")
        return f"❌ Қате: {e}"