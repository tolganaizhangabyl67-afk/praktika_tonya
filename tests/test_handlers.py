import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import Message, User, Chat

def make_message(text: str, user_id: int = 123, username: str = "testuser") -> MagicMock:
    message = MagicMock(spec=Message)
    message.text = text
    message.from_user = MagicMock(spec=User)
    message.from_user.id = user_id
    message.from_user.username = username
    message.from_user.full_name = "Test User"
    message.from_user.first_name = "Test"
    message.chat = MagicMock(spec=Chat)
    message.chat.id = user_id
    message.bot = AsyncMock()
    message.answer = AsyncMock(return_value=MagicMock(edit_text=AsyncMock()))
    return message

@pytest.mark.asyncio
async def test_start_command():
    from handlers.common import cmd_start
    message = make_message("/start")
    await cmd_start(message)
    message.answer.assert_called_once()

@pytest.mark.asyncio
async def test_help_command():
    from handlers.common import cmd_help
    message = make_message("/help")
    await cmd_help(message)
    message.answer.assert_called_once()

@pytest.mark.asyncio
async def test_rate_limiter_blocks():
    from utils.rate_limiter import RateLimiter
    limiter = RateLimiter()
    limiter.USER_LIMIT = 3
    for i in range(3):
        allowed, _ = limiter.is_allowed(999, 999)
        assert allowed == True
    allowed, reason = limiter.is_allowed(999, 999)
    assert allowed == False

@pytest.mark.asyncio
async def test_ai_response_under_5_seconds():
    import time
    from services.groq_service import GroqService
    service = GroqService()

    async def mock_stream(*args, **kwargs):
        yield "Привет"
        yield "!"

    with patch.object(service, 'get_response_stream', side_effect=mock_stream):
        start = time.time()
        result = await service.get_response("привет")
        elapsed = time.time() - start

    assert elapsed < 5
    assert isinstance(result, str)

@pytest.mark.asyncio
async def test_search_returns_results():
    from services.search_service import search_web
    with patch("services.search_service.DDGS") as mock_ddgs:
        mock_ddgs.return_value.__enter__.return_value.text.return_value = [
            {"title": "Test", "href": "https://test.com", "body": "Test result"}
        ]
        results = search_web("test query")
        assert len(results) > 0
        assert "title" in results[0]
