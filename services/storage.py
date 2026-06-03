import asyncpg
import config
from utils.logger import get_logger
from aiogram.fsm.storage.memory import MemoryStorage

logger = get_logger(__name__)

# Aiogram FSM storage
storage = MemoryStorage()

# Жаһандық пул айнымалысы
db_pool = None


async def init_db_pool():
    global db_pool
    if db_pool is None:
        try:
            db_pool = await asyncpg.create_pool(
                config.DB_URL,
                min_size=1,
                max_size=10
            )
            logger.info("🚀 PostgreSQL Connection Pool сәтті іске қосылды!")
        except Exception as e:
            logger.error(f"❌ Пулды іске қосу қатесі: {e}")
            raise


async def close_db_pool():
    global db_pool
    if db_pool:
        await db_pool.close()
        db_pool = None
        logger.info("🔒 PostgreSQL Connection Pool жабылды.")


async def get_connection():
    global db_pool
    if db_pool is None:
        raise RuntimeError("DB пул іске қосылмаған!")
    return db_pool.acquire()


async def execute(query: str, *args):
    async with db_pool.acquire() as conn:
        return await conn.execute(query, *args)


async def fetch(query: str, *args):
    async with db_pool.acquire() as conn:
        return await conn.fetch(query, *args)


async def fetchrow(query: str, *args):
    async with db_pool.acquire() as conn:
        return await conn.fetchrow(query, *args)


async def fetchval(query: str, *args):
    async with db_pool.acquire() as conn:
        return await conn.fetchval(query, *args)


# ✅ Chat.py қолданатын функциялар
async def save_user(username: str, full_name: str, user_id: int):
    try:
        await execute("""
            INSERT INTO users (user_id, username, full_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO UPDATE
            SET username = $2, full_name = $3
        """, user_id, username, full_name)
    except Exception as e:
        logger.error(f"save_user қатесі: {e}")


async def save_message(username: str, user_message: str, bot_response: str, user_id: int):
    try:
        await execute("""
            INSERT INTO messages (user_id, username, message, response)
            VALUES ($1, $2, $3, $4)
        """, user_id, username, user_message, bot_response)
    except Exception as e:
        logger.error(f"save_message қатесі: {e}")


async def get_chat_history(username: str, limit: int = 10):
    try:
        rows = await fetch("""
            SELECT message, response FROM messages
            WHERE username = $1
            ORDER BY id DESC LIMIT $2
        """, username, limit)
        history = []
        for row in reversed(rows):
            history.append({"role": "user", "content": row["message"]})
            history.append({"role": "assistant", "content": row["response"]})
        return history
    except Exception as e:
        logger.error(f"get_chat_history қатесі: {e}")
        return []