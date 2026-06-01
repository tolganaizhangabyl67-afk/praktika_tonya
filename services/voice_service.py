import os
import logging
from groq import AsyncGroq
import config

logger = logging.getLogger(__name__)
client = AsyncGroq(api_key=config.GROQ_API_KEY)

async def transcribe_voice(file_path: str) -> str:
    try:
        abs_file = os.path.abspath(file_path)
        with open(abs_file, "rb") as f:
            transcription = await client.audio.transcriptions.create(
                file=("audio.ogg", f),
                model="whisper-large-v3"
            )
        if os.path.exists(abs_file):
            os.remove(abs_file)
        return transcription.text
    except Exception as e:
        logger.error("Whisper қатесі: " + str(e))
        return "Қате: " + str(e)