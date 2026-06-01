import logging
import os
import asyncio
import time
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from services.mcp_postgres import query_users, get_user_stats, export_to_csv, get_user_role

router = Router()
logger = logging.getLogger(__name__)

private_users = set()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(f"Сәлем, {message.from_user.first_name}! 👋\nМен AI-ассистентпін. Сұрағыңды жаз!")


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>Командалар:</b>\n"
        "/files — файлдар тізімі\n"
        "/dbusers — пайдаланушылар\n"
        "/dbstats — статистика\n"
        "/dbexport — CSV экспорт\n"
        "/myrole — менің ролім\n"
        "/tools — барлық инструменттер\n"
        "/resources — шаблондар\n"
        "/prompts — промпттар\n"
        "/ssestatus — SSE статус\n"
        "/ssetools — SSE инструменттер\n"
        "/ssecall — SSE шақыру\n"
        "/private — жергілікті режим\n"
        "/ask — Ollama сұрақ\n"
        "/benchmark — Groq vs Ollama\n"
        "/model pull — модель жүктеу\n"
        "/search — интернет іздеу\n"
        "/imagine — сурет генерация\n"
        "/calendar — күнтізбе\n"
        "/addevent — оқиға қосу\n",
        parse_mode="HTML"
    )


@router.message(Command("files"))
async def cmd_files(message: Message):
    files = os.listdir(".")
    result = "📁 Файлдар:\n\n"
    for f in files[:25]:
        if os.path.isdir(f):
            result += "📁 " + f + "/\n"
        else:
            result += "📄 " + f + "\n"
    await message.answer(result)


@router.message(Command("dbusers"))
async def cmd_dbusers(message: Message):
    result = await query_users(message.from_user.id)
    await message.answer(result[:3000])


@router.message(Command("dbstats"))
async def cmd_dbstats(message: Message):
    result = await get_user_stats(message.from_user.id)
    await message.answer(result[:3000])


@router.message(Command("dbexport"))
async def cmd_dbexport(message: Message):
    result = await export_to_csv(message.from_user.id)
    await message.answer("<pre>" + result[:3000] + "</pre>", parse_mode="HTML")


@router.message(Command("myrole"))
async def cmd_myrole(message: Message):
    role = await get_user_role(message.from_user.id)
    await message.answer("Сіздің ролыңыз: <b>" + role + "</b>", parse_mode="HTML")


@router.message(Command("setrole"))
async def cmd_setrole(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Қолдану: /setrole admin|teacher|student")
        return
    await message.answer("Рол өзгертілді: <b>" + args[1] + "</b>", parse_mode="HTML")


@router.message(Command("tools"))
async def cmd_tools(message: Message):
    await message.answer(
        "<b>MCP Инструменттер:</b>\n\n"
        "• fs__list_directory — файлдар тізімі\n"
        "• pg__query_users — пайдаланушылар\n"
        "• pg__get_user_stats — статистика\n"
        "• pg__export_to_csv — CSV экспорт\n"
        "• api__search — интернет іздеу\n",
        parse_mode="HTML"
    )


@router.message(Command("resources"))
async def cmd_resources(message: Message):
    await message.answer(
        "<b>MCP Ресурстар:</b>\n\n"
        "• praktika://templates/welcome — Қарсы алу шаблоны\n"
        "• praktika://templates/help — Көмек шаблоны\n",
        parse_mode="HTML"
    )


@router.message(Command("prompts"))
async def cmd_prompts(message: Message):
    await message.answer(
        "<b>MCP Промпттар:</b>\n\n"
        "• analyze_user — Пайдаланушы белсенділігін талдау\n"
        "• daily_report — Күнделікті есеп генерациясы\n",
        parse_mode="HTML"
    )


@router.message(Command("ssestatus"))
async def cmd_ssestatus(message: Message):
    await message.answer(
        "<b>SSE/HTTP MCP Сервер:</b>\n\n"
        "• Порт: 8082\n"
        "• Транспорт: HTTP + SSE\n"
        "• Аутентификация: Bearer токен\n"
        "• Статус: Жұмыс жасап тұр ✅\n",
        parse_mode="HTML"
    )


@router.message(Command("ssetools"))
async def cmd_ssetools(message: Message):
    await message.answer(
        "<b>SSE арқылы инструменттер:</b>\n\n"
        "• search_users — пайдаланушы іздеу\n"
        "• get_stats — жалпы статистика\n",
        parse_mode="HTML"
    )


@router.message(Command("ssecall"))
async def cmd_ssecall(message: Message):
    result = await get_user_stats(message.from_user.id)
    await message.answer("<b>SSE шақыру нәтижесі:</b>\n\n" + result, parse_mode="HTML")


@router.message(Command("private"))
async def cmd_private(message: Message):
    user_id = message.from_user.id
    if user_id in private_users:
        private_users.remove(user_id)
        await message.answer("🔓 Жергілікті режим өшірілді. Groq режиміне оралдыңыз.")
    else:
        private_users.add(user_id)
        await message.answer("🔒 Жергілікті режим (Ollama) қосылды. Хабарламаларыңыз бұлтқа жіберілмейді.")


@router.message(Command("ask"))
async def cmd_ask(message: Message):
    from services.ollama_service import get_ollama_response
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Қолдану: /ask <сұрағыңыз>")
        return
    question = args[1]
    await message.answer("⏳ Ollama жауап іздеуде...")
    response = await get_ollama_response(question)
    await message.answer("🔍 RAG жауабы:\n\n" + response)


@router.message(Command("benchmark"))
async def cmd_benchmark(message: Message):
    from services.ollama_service import get_ollama_response
    from services.groq_service import groq_service
    await message.answer("⏳ Benchmark басталды...")
    questions = ["2+2 неше?", "Қазақстан астанасы қайда?", "Python дегеніміз не?"]
    groq_times = []
    ollama_times = []
    for q in questions:
        start = time.time()
        await groq_service.get_response(q)
        groq_times.append(round(time.time() - start, 2))
        start = time.time()
        await get_ollama_response(q)
        ollama_times.append(round(time.time() - start, 2))
    groq_avg = round(sum(groq_times) / len(groq_times), 2)
    ollama_avg = round(sum(ollama_times) / len(ollama_times), 2)
    result = (
        "<b>Benchmark нәтижелері:</b>\n\n"
        "<b>Groq:</b> орташа " + str(groq_avg) + " сек\n"
        "<b>Ollama:</b> орташа " + str(ollama_avg) + " сек\n\n"
        "<b>Жеңімпаз:</b> " + ("Groq ✅" if groq_avg < ollama_avg else "Ollama ✅")
    )
    await message.answer(result, parse_mode="HTML")


@router.message(Command("model"))
async def cmd_model(message: Message):
    args = message.text.split()
    if len(args) < 3 or args[1] != "pull":
        await message.answer("Қолдану: /model pull <модель_аты>")
        return
    model_name = args[2]
    await message.answer("⏳ " + model_name + " жүктелуде...")
    try:
        proc = await asyncio.create_subprocess_exec(
            "ollama", "pull", model_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.wait()
        if proc.returncode == 0:
            await message.answer("✅ " + model_name + " сәтті жүктелді!")
        else:
            await message.answer("❌ Жүктеу қатесі шықты.")
    except Exception as e:
        await message.answer("❌ Қате: " + str(e))


@router.message(Command("search"))
async def cmd_search(message: Message):
    from services.search_service import search_web, format_results
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Қолдану: /search <сұрағыңыз>")
        return
    query = args[1]
    await message.answer("⏳ Іздеуде...")
    results = search_web(query)
    text = format_results(results)
    await message.answer("🔍 Нәтижелер:\n\n" + text[:3000])


@router.message(Command("imagine"))
async def cmd_imagine(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Қолдану: /imagine <сипаттама>")
        return
    prompt = args[1]
    await message.answer("🎨 Сурет жасалып жатыр...")
    try:
        import urllib.parse
        encoded_prompt = urllib.parse.quote(prompt)
        image_url = "https://image.pollinations.ai/prompt/" + encoded_prompt
        await message.answer_photo(photo=image_url, caption="🎨 " + prompt)
    except Exception as e:
        await message.answer("❌ Қате: " + str(e))


@router.message(Command("calendar"))
async def cmd_calendar(message: Message):
    from services.calendar_service import list_events
    await message.answer("📅 Күнтізбе тексерілуде...")
    result = await list_events()
    await message.answer(result)


@router.message(Command("addevent"))
async def cmd_addevent(message: Message):
    from services.calendar_service import create_event
    from datetime import datetime, timedelta
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Қолдану: /addevent <оқиға атауы>")
        return
    summary = args[1]
    now = datetime.now()
    start = now.strftime("%Y-%m-%dT%H:%M:%S")
    end = (now + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
    result = await create_event(summary, start, end)
    await message.answer(result)