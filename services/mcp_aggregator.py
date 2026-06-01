import logging
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWED_DIR = BASE_DIR

async def call_tool(server_command: str, server_args: list, tool_name: str, tool_args: dict) -> str:
    try:
        server_params = StdioServerParameters(
            command=server_command,
            args=server_args
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=tool_args)
                return result.content[0].text
    except Exception as e:
        logger.error(f"MCP ошибка [{tool_name}]: {e}")
        return f"Ошибка: {e}"

async def list_all_tools() -> str:
    tools = []
    try:
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", ALLOWED_DIR]
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                for tool in result.tools:
                    tools.append(f"fs__{tool.name} — {tool.description}")
    except Exception as e:
        tools.append(f"fs__ сервер недоступен: {e}")

    tools.append("pg__query_users — список всех пользователей")
    tools.append("pg__get_user_stats — статистика пользователя")
    tools.append("pg__export_to_csv — экспорт в CSV")
    tools.append("api__search — поиск в интернете через DuckDuckGo")

    text = "🔧 Доступные инструменты:\n\n" + "\n".join(f"• {t}" for t in tools)
    return text[:4000]

async def route_tool(tool_name: str, tool_args: dict, user_id: int) -> str:
    if tool_name.startswith("fs__"):
        actual_tool = tool_name[4:]
        return await call_tool(
            "npx",
            ["-y", "@modelcontextprotocol/server-filesystem", ALLOWED_DIR],
            actual_tool,
            tool_args
        )
    elif tool_name.startswith("pg__"):
        from services.mcp_postgres import query_users, get_user_stats, export_to_csv
        actual_tool = tool_name[4:]
        if actual_tool == "query_users":
            return await query_users(user_id)
        elif actual_tool == "get_user_stats":
            return await get_user_stats(user_id)
        elif actual_tool == "export_to_csv":
            return await export_to_csv(user_id)
        return "инструмент не найден"
    elif tool_name.startswith("api__"):
        from duckduckgo_search import DDGS
        query = tool_args.get("query", "")
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
                if not results:
                    return "Ничего не найдено."
                return "\n".join(f"- {r.get('body', '')}" for r in results)
        except Exception as e:
            return f"Ошибка поиска: {e}"
    return f"⛔ Неизвестный префикс: {tool_name}"