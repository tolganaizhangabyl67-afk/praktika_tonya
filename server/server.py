import asyncpg
import asyncio
import config
from utils.logger import get_logger

logger = get_logger(__name__)
# Жаһандық пул айнымалысы
db_pool = None

async def init_db_pool():
    """Бот іске қосылғанда пул бір-ақ рет ашылады"""
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

async def close_db_pool():
    """Бот тоқтағанда пул жабылады"""
    global db_pool
    if db_pool:
        await db_pool.close()
        logger.info("🔒 PostgreSQL Connection Pool жабылды.")

# Егер серверді іске қосатын негізгі функцияң болса, 
# оның басына init_db_pool() қосып қою керек.