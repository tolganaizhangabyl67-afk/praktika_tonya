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
    message.answer = AsyncMock()
    return message


@pytest.mark.asyncio
async def test_start_returns_greeting():
    from handlers.common import cmd_start
    message = make_message("/start")
    await cmd_start(message)
    message.answer.assert_called_once()
    call_text = message.answer.call_args[0][0]
    assert "Сәлем" in call_text or "AI" in call_text


@pytest.mark.asyncio
async def test_help_returns_commands():
    from handlers.common import cmd_help
    message = make_message("/help")
    await cmd_help(message)
    message.answer.assert_called_once()
    call_text = message.answer.call_args[1].get("text", "") or message.answer.call_args[0][0]
    assert len(call_text) > 10


@pytest.mark.asyncio
async def test_dbstats_returns_data():
    from handlers.common import cmd_dbstats
    message = make_message("/dbstats")
    with patch("handlers.common.get_user_stats", new_callable=AsyncMock) as mock_stats:
        mock_stats.return_value = "Статистика:\nАты: Test\nХабарламалар: 5"
        await cmd_dbstats(message)
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_myrole_returns_role():
    from handlers.common import cmd_myrole
    message = make_message("/myrole")
    with patch("handlers.common.get_user_role", new_callable=AsyncMock) as mock_role:
        mock_role.return_value = "student"
        await cmd_myrole(message)
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_search_command():
    from handlers.common import cmd_search
    message = make_message("/search Казахстан")
    with patch("services.search_service.DDGS") as mock_ddgs:
        mock_ddgs.return_value.__enter__.return_value.text.return_value = [
            {"title": "Test", "href": "https://test.com", "body": "Test result"}
        ]
        await cmd_search(message)
    message.answer.assert_called()


@pytest.mark.asyncio
async def test_full_chat_flow():
    from handlers.chat import handle_text_message
    message = make_message("Привет")
    with patch("services.storage.storage.save_user", new_callable=AsyncMock), \
         patch("services.storage.storage.get_chat_history", new_callable=AsyncMock, return_value=[]), \
         patch("services.storage.storage.save_message", new_callable=AsyncMock), \
         patch("services.groq_service.groq_service.get_chat_response", new_callable=AsyncMock, return_value="Привет!"):
        await handle_text_message(message)
    message.answer.assert_called_once()