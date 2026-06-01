import time
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        # {user_id: [timestamps]}
        self.user_requests = defaultdict(list)
        self.chat_requests = defaultdict(list)
        
        self.USER_LIMIT = 10    # запросов в минуту на пользователя
        self.CHAT_LIMIT = 50    # запросов в минуту на чат

    def _clean_old(self, timestamps: list) -> list:
        """Убираем запросы старше 1 минуты"""
        now = time.time()
        return [t for t in timestamps if now - t < 60]

    def is_allowed(self, user_id: int, chat_id: int) -> tuple[bool, str]:
        """Проверяем можно ли обработать запрос"""
        now = time.time()

        # Чистим старые записи
        self.user_requests[user_id] = self._clean_old(self.user_requests[user_id])
        self.chat_requests[chat_id] = self._clean_old(self.chat_requests[chat_id])

        # Проверяем лимит пользователя
        if len(self.user_requests[user_id]) >= self.USER_LIMIT:
            logger.warning(f"Rate limit: user_id={user_id} превысил лимит")
            return False, f"⛔ Слишком много запросов! Подожди минуту. ({self.USER_LIMIT}/мин)"

        # Проверяем лимит чата
        if len(self.chat_requests[chat_id]) >= self.CHAT_LIMIT:
            logger.warning(f"Rate limit: chat_id={chat_id} превысил лимит")
            return False, f"⛔ Чат перегружен! Подожди минуту. ({self.CHAT_LIMIT}/мин)"

        # Всё ок — записываем запрос
        self.user_requests[user_id].append(now)
        self.chat_requests[chat_id].append(now)
        return True, ""

rate_limiter = RateLimiter()
