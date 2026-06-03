import asyncio
import logging
import json
import urllib.request
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from config import BOT_TOKEN
from handlers import common, chat
from utils.logger import setup_logger
from services.storage import storage

setup_logger()

WEBHOOK_PORT = 8080

async def get_ngrok_url() -> str:
    await asyncio.sleep(2)
    try:
        with urllib.request.urlopen("http://localhost:4040/api/tunnels") as r:
            data = json.loads(r.read())
            url = data["tunnels"][0]["public_url"]
            if url.startswith("http://"):
                url = url.replace("http://", "https://")
            return url
    except Exception as e:
        logging.error("ngrok URL алу қатесі: " + str(e))
        return None

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp = Dispatcher(storage=storage)
    dp.include_router(common.router)
    dp.include_router(chat.router)

    logging.info("ngrok URL алынуда...")
    webhook_url = await get_ngrok_url()

    if not webhook_url:
        logging.warning("ngrok жоқ — polling режимінде іске қосылды")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
        return

    webhook_path = "/webhook"
    full_url = webhook_url + webhook_path

    await bot.set_webhook(full_url)
    logging.info("Webhook орнатылды: " + full_url)

    app = web.Application()
    handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    handler.register(app, path=webhook_path)
    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", WEBHOOK_PORT)
    await site.start()

    logging.info("Публичный URL: " + full_url)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())