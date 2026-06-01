import logging
import time
from ddgs import DDGS

logger = logging.getLogger(__name__)

# Простой кэш в памяти: {query: (result, timestamp)}
search_cache = {}
CACHE_TTL = 3600  # 1 час

def get_cached(query: str):
    if query in search_cache:
        result, timestamp = search_cache[query]
        if time.time() - timestamp < CACHE_TTL:
            logger.info(f"Кэш HIT: {query}")
            return result
        else:
            del search_cache[query]
    return None

def set_cache(query: str, result: str):
    search_cache[query] = (result, time.time())
    logger.info(f"Кэш SET: {query}")

def search_web(query: str, max_results: int = 5) -> list:
    """Поиск с кэшированием"""
    cached = get_cached(query)
    if cached:
        return cached

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            formatted = [
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")
                }
                for r in results
            ]
            set_cache(query, formatted)
            return formatted
    except Exception as e:
        logger.error(f"Поиск ошибка: {e}")
        return []

def format_results(results: list) -> str:
    if not results:
        return "Ничего не найдено."
    text = ""
    for i, r in enumerate(results, 1):
        text += f"{i}. {r['title']}\n{r['url']}\n{r['snippet']}\n\n"
    return text.strip()
