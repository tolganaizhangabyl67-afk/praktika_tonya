import logging
import aiohttp
import traceback
from ddgs import DDGS

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3"

SIMPLE_WORDS = ["привет", "сәлем", "hello", "hi", "ок", "окей", "да", "нет", "жақсы", "спасибо", "рахмет", "пока", "как дела", "қалайсың"]

def search_web(query: str) -> str:
    if any(w in query.lower() for w in SIMPLE_WORDS):
        return ""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if not results:
                return ""
            context = "Интернеттен табылған ақпарат:\n"
            for r in results:
                context += "- " + r.get("body", "") + "\n"
            return context
    except Exception:
        return ""

async def get_ollama_response(user_message: str, history: list = []) -> str:
    try:
        web_info = search_web(user_message)

        user_content = user_message
        if web_info:
            user_content = web_info + "\n\nСұрақ: " + user_message

        messages = [
            {
                "role": "system",
                "content": (
                    "Сен — жергілікті AI ассистентсің. "
                    "Пайдаланушы қай тілде жазса, сол тілде жауап бер. "
                    "Егер интернет ақпараты берілсе — тек сол ақпарат негізінде жауап бер. "
                    "Егер ақпарат берілмесе — қысқа және достық жауап бер. "
                    "Ешқашан өтірік немесе болжамды ақпарат берме."
                )
            }
        ]
        messages.extend(history)
        messages.append({"role": "user", "content": user_content})

        timeout = aiohttp.ClientTimeout(total=300)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                OLLAMA_URL + "/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False
                }
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    logger.error("Ollama HTTP қате: " + str(resp.status) + " | " + text)
                    return "Ollama қатесі: HTTP " + str(resp.status)
                data = await resp.json()
                return data["message"]["content"]

    except aiohttp.ClientConnectorError as e:
        logger.error("Ollama қосылу қатесі: " + str(e))
        return "Ollama іске қосылмаған. Терминалда 'ollama serve' жазыңыз."
    except Exception as e:
        logger.error("Ollama қатесі: " + str(e))
        logger.error(traceback.format_exc())
        return "Ollama қатесі: " + str(e)

async def check_ollama() -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(OLLAMA_URL + "/api/tags") as resp:
                return resp.status == 200
    except Exception:
        return False