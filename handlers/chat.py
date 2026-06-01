import os
import base64
from aiogram import Router, F, Bot
from aiogram.types import Message
from services.groq_service import groq_service
from services.storage import storage
from utils.logger import get_logger
from handlers.common import private_users

logger = get_logger(__name__)
router = Router()


@router.message(F.voice)
async def handle_voice_message(message: Message, bot: Bot):
    username = message.from_user.username or f"user_{message.from_user.id}"
    full_name = message.from_user.full_name or "Пайдаланушы"
    user_id = message.from_user.id

    await storage.save_user(username=username, full_name=full_name, user_id=user_id)

    os.makedirs("downloads", exist_ok=True)
    ogg_path = f"downloads/{message.voice.file_id}.ogg"

    try:
        file_info = await bot.get_file(message.voice.file_id)
        await bot.download_file(file_info.file_path, ogg_path)

        result = await groq_service.transcribe_audio(ogg_path)
        user_text = result["text"]
        language = result["language"]

        if not user_text:
            await message.answer("Дауысыңызды анықтау мүмкін болмады.")
            return

        history = await storage.get_chat_history(username) or []
        bot_response = await groq_service.get_chat_response(user_text, history, language=language)

        await storage.save_message(username=username, user_message=user_text, bot_response=bot_response, user_id=user_id)
        await message.answer(bot_response)

    except Exception as e:
        logger.error("Аудио өңдеу қатесі: " + str(e))
        await message.answer("Қате шықты.")
    finally:
        if os.path.exists(ogg_path):
            os.remove(ogg_path)


@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot):
    username = message.from_user.username or f"user_{message.from_user.id}"
    full_name = message.from_user.full_name or "Пайдаланушы"
    user_id = message.from_user.id

    await storage.save_user(username=username, full_name=full_name, user_id=user_id)
    await message.answer("🔍 Сурет талданып жатыр...")

    try:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        os.makedirs("downloads", exist_ok=True)
        photo_path = f"downloads/{photo.file_id}.jpg"
        await bot.download_file(file_info.file_path, photo_path)

        with open(photo_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        from groq import AsyncGroq
        import config
        client = AsyncGroq(api_key=config.GROQ_API_KEY)

        caption = message.caption or "Бұл суретте не бар? Қазақша немесе орысша жауап бер."

        response = await client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:image/jpeg;base64," + image_data
                            }
                        },
                        {
                            "type": "text",
                            "text": caption
                        }
                    ]
                }
            ],
            max_tokens=1024
        )

        bot_response = response.choices[0].message.content
        await storage.save_message(username=username, user_message="[сурет]", bot_response=bot_response, user_id=user_id)
        await message.answer("🖼 " + bot_response)

        if os.path.exists(photo_path):
            os.remove(photo_path)

    except Exception as e:
        logger.error("Сурет өңдеу қатесі: " + str(e))
        await message.answer("Суретті талдау кезінде қате шықты: " + str(e))


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text_message(message: Message):
    username = message.from_user.username or f"user_{message.from_user.id}"
    full_name = message.from_user.full_name or "Пайдаланушы"
    user_id = message.from_user.id

    await storage.save_user(username=username, full_name=full_name, user_id=user_id)

    user_text = message.text
    history = await storage.get_chat_history(username) or []

    from services.ollama_service import get_ollama_response

    if user_id in private_users:
        bot_response = await get_ollama_response(user_text, history)
        indicator = "🔒 "
    else:
        bot_response = await groq_service.get_chat_response(user_text, history)
        indicator = ""

    await storage.save_message(username=username, user_message=user_text, bot_response=bot_response, user_id=user_id)
    await message.answer(indicator + bot_response)