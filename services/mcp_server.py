from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
import asyncpg
import config
import logging

logger = logging.getLogger(__name__)

app = Server("Praktika-mcp")

@app.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="search_users",
            description="Поиск пользователей в базе данных",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "имя или username для поиска"}
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

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        conn = await asyncpg.connect(config.DB_URL)
        if name == "search_users":
            query = arguments.get("query", "")
            rows = await conn.fetch(
                "SELECT username, full_name FROM users WHERE username ILIKE $1 OR full_name ILIKE $1",
                f"%{query}%"
            )
            await conn.close()
            if not rows:
                return [types.TextContent(type="text", text="Никого не найдено.")]
            result = "\n".join(f"{r['full_name']} (@{r['username']})" for r in rows)
            return [types.TextContent(type="text", text=result)]
        elif name == "get_stats":
            rows = await conn.fetch("SELECT COUNT(*) as cnt FROM users")
            await conn.close()
            return [types.TextContent(type="text", text=f"Всего пользователей: {rows[0]['cnt']}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Ошибка: {e}")]
    return [types.TextContent(type="text", text="Инструмент не найден")]

@app.list_resources()
async def list_resources():
    return [
        types.Resource(
            uri="praktika://templates/welcome",
            name="Шаблон приветствия",
            description="Шаблон приветственного сообщения",
            mimeType="text/plain"
        ),
        types.Resource(
            uri="praktika://templates/help",
            name="Шаблон помощи",
            description="Шаблон сообщения со списком команд",
            mimeType="text/plain"
        )
    ]

@app.read_resource()
async def read_resource(uri: str):
    if str(uri) == "praktika://templates/welcome":
        return "Привет! Я Tonya — ИИ-ассистент. Задавай любые вопросы!"
    elif str(uri) == "praktika://templates/help":
        return (
            "Доступные команды:\n"
            "/start — начать\n"
            "/reset — сбросить историю\n"
            "/files — файлы проекта\n"
            "/tools — список MCP инструментов\n"
            "/users — список пользователей\n"
            "/mystats — моя статистика\n"
            "/export — экспорт в CSV\n"
            "/search — поиск в интернете\n"
            "/private — приватный режим"
        )
    raise ValueError(f"Ресурс не найден: {uri}")

@app.list_prompts()
async def list_prompts():
    return [
        types.Prompt(
            name="analyze_user",
            description="Промпт для анализа активности пользователя",
            arguments=[
                types.PromptArgument(name="username", description="Username пользователя", required=True)
            ]
        ),
        types.Prompt(
            name="daily_report",
            description="Промпт для генерации ежедневного отчёта",
            arguments=[]
        )
    ]

@app.get_prompt()
async def get_prompt(name: str, arguments: dict):
    if name == "analyze_user":
        username = arguments.get("username", "unknown")
        return types.GetPromptResult(
            description="Анализ пользователя",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Проанализируй активность пользователя @{username} в боте Tonya. Дай рекомендации."
                    )
                )
            ]
        )
    elif name == "daily_report":
        return types.GetPromptResult(
            description="Ежедневный отчёт",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text="Сгенерируй краткий ежедневный отчёт по активности пользователей бота Tonya."
                    )
                )
            ]
        )
    raise ValueError(f"Промпт не найден: {name}")

async def run():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())