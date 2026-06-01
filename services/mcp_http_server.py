from mcp.server import Server
from mcp.server.sse import SseServerTransport
from aiohttp import web
import asyncpg
import config
import logging
from mcp import types

logger = logging.getLogger(__name__)

app_server = Server("Praktika-mcp-http")

@app_server.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="search_users",
            description="Поиск пользователей в базе данных",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_stats",
            description="Получить статистику бота",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@app_server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "search_users":
        query = arguments.get("query", "")
        try:
            conn = await asyncpg.connect(config.DB_URL)
            rows = await conn.fetch(
                "SELECT username, full_name, role, message_count FROM users WHERE username ILIKE $1 OR full_name ILIKE $1",
                f"%{query}%"
            )
            await conn.close()
            if not rows:
                return [types.TextContent(type="text", text="Никого не найдено.")]
            result = "\n".join(f"{r['full_name']} (@{r['username']}) [{r['role']}]" for r in rows)
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Ошибка: {e}")]

    elif name == "get_stats":
        try:
            conn = await asyncpg.connect(config.DB_URL)
            count = await conn.fetchval("SELECT COUNT(*) FROM users")
            total_messages = await conn.fetchval("SELECT SUM(message_count) FROM users")
            await conn.close()
            return [types.TextContent(
                type="text",
                text=f"Пользователей: {count}\nВсего сообщений: {total_messages}"
            )]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Ошибка: {e}")]

    return [types.TextContent(type="text", text="Инструмент не найден")]

async def handle_sse(request: web.Request) -> web.Response:
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {config.MCP_SECRET_TOKEN}":
        return web.Response(status=401, text="Unauthorized")

    transport = SseServerTransport("/messages")
    async with transport.connect_sse(request) as (read, write):
        await app_server.run(read, write, app_server.create_initialization_options())
    return web.Response()

def create_mcp_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/sse", handle_sse)
    return app
