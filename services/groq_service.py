from groq import AsyncGroq
from ddgs import DDGS
import config
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

SEARCH_KEYWORDS = [
    "погода", "сегодня", "завтра", "сейчас", "коап", "статья", "штраф",
    "курс", "валюта", "новости", "цена", "закон", "2026", "число", "дата",
    "день", "число", "месяц"
]

SIMPLE_KEYWORDS = ["привет", "пока", "спасибо", "ок", "окей", "да", "нет", "помоги"]

class GroqService:
    def __init__(self):
        self.client = AsyncGroq(api_key=config.GROQ_API_KEY)
        self.model_smart = config.GROQ_MODEL
        self.model_fast = config.GROQ_MODEL_FAST

    def pick_model(self, text: str) -> str:
        text_lower = text.lower()
        if len(text) < 30 or any(w in text_lower for w in SIMPLE_KEYWORDS):
            logger.info("Роутер: быстрая модель")
            return self.model_fast
        logger.info("Роутер: умная модель")
        return self.model_smart

    def needs_search(self, text: str) -> bool:
        return any(w in text.lower() for w in SEARCH_KEYWORDS)

    def search_internet(self, query: str) -> str:
        try:
            if any(w in query.lower() for w in ["коап", "статья", "штраф"]):
                query += " Казахстан"
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
                if not results:
                    return ""
                context = "ДАННЫЕ ИЗ СЕТИ:\n"
                for r in results:
                    context += "- " + r.get("body", "") + "\n"
                return context
        except Exception:
            return ""

    def get_system_prompt(self) -> str:
        now = datetime.now()
        days_ru = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
        months_ru = ["января", "февраля", "марта", "апреля", "мая", "июня",
                     "июля", "августа", "сентября", "октября", "ноября", "декабря"]
        day_name = days_ru[now.weekday()]
        month_name = months_ru[now.month - 1]
        date_str = str(now.day) + " " + month_name + " " + str(now.year) + " года, " + day_name
        return "Ты — ИИ-ассистент Praktika. Отвечаешь чётко, без воды. Сегодня " + date_str + ". Текущий год — " + str(now.year) + "."

    async def get_response_stream(self, user_message: str, history: list = []):
        web_info = ""
        if self.needs_search(user_message):
            web_info = self.search_internet(user_message)

        user_content = user_message
        if web_info:
            user_content = web_info + "\n\nВопрос: " + user_message

        messages = [{"role": "system", "content": self.get_system_prompt()}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_content})

        primary_model = self.pick_model(user_message)
        fallback_model = self.model_fast if primary_model == self.model_smart else self.model_smart

        for model in [primary_model, fallback_model]:
            try:
                logger.info("Пробуем модель: " + model)
                stream = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.1,
                    stream=True
                )
                async for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta
                return
            except Exception as e:
                logger.warning("Модель " + model + " недоступна: " + str(e))
                continue

        yield "Ошибка: все модели недоступны. Попробуйте позже."

    async def get_response(self, user_message: str, history: list = []) -> str:
        result = ""
        async for chunk in self.get_response_stream(user_message, history):
            result += chunk
        return result

    async def get_chat_response(self, user_message: str, history: list = [], language: str = None) -> str:
        return await self.get_response(user_message, history)

    async def transcribe_audio(self, file_path: str) -> dict:
        with open(file_path, "rb") as f:
            result = await self.client.audio.transcriptions.create(
                file=f,
                model="whisper-large-v3",
                response_format="verbose_json"
            )
        return {"text": result.text, "language": result.language}


groq_service = GroqService()