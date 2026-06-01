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
async def test_files_command():
    from handlers.common import cmd_files
    message = make_message("/files")
    await cmd_files(message)
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_tools_command():
    from handlers.common import cmd_tools
    message = make_message("/tools")
    await cmd_tools(message)
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_resources_command():
    from handlers.common import cmd_resources
    message = make_message("/resources")
    await cmd_resources(message)
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_prompts_command():
    from handlers.common import cmd_prompts
    message = make_message("/prompts")
    await cmd_prompts(message)
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_ssestatus_command():
    from handlers.common import cmd_ssestatus
    message = make_message("/ssestatus")
    await cmd_ssestatus(message)
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_ssetools_command():
    from handlers.common import cmd_ssetools
    message = make_message("/ssetools")
    await cmd_ssetools(message)
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_private_command_on():
    from handlers.common import cmd_private, private_users
    message = make_message("/private")
    private_users.discard(123)
    await cmd_private(message)
    message.answer.assert_called_once()
    assert 123 in private_users


@pytest.mark.asyncio
async def test_private_command_off():
    from handlers.common import cmd_private, private_users
    message = make_message("/private")
    private_users.add(123)
    await cmd_private(message)
    message.answer.assert_called_once()
    assert 123 not in private_users


@pytest.mark.asyncio
async def test_setrole_command():
    from handlers.common import cmd_setrole
    message = make_message("/setrole admin")
    await cmd_setrole(message)
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_setrole_no_args():
    from handlers.common import cmd_setrole
    message = make_message("/setrole")
    await cmd_setrole(message)
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_ssecall_command():
    from handlers.common import cmd_ssecall
    message = make_message("/ssecall")
    with patch("handlers.common.get_user_stats", new_callable=AsyncMock) as mock:
        mock.return_value = "Статистика: 5 хабарлама"
        await cmd_ssecall(message)
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_ask_command():
    from handlers.common import cmd_ask
    message = make_message("/ask Сәлем")
    with patch("services.ollama_service.get_ollama_response", new_callable=AsyncMock) as mock:
        mock.return_value = "Сәлем!"
        await cmd_ask(message)
    message.answer.assert_called()


@pytest.mark.asyncio
async def test_ask_no_args():
    from handlers.common import cmd_ask
    message = make_message("/ask")
    await cmd_ask(message)
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_imagine_command():
    from handlers.common import cmd_imagine
    message = make_message("/imagine cat")
    message.answer_photo = AsyncMock()
    await cmd_imagine(message)
    message.answer_photo.assert_called_once()


@pytest.mark.asyncio
async def test_imagine_no_args():
    from handlers.common import cmd_imagine
    message = make_message("/imagine")
    await cmd_imagine(message)
    message.answer.assert_called_once()


def test_search_keywords():
    from services.groq_service import GroqService
    service = GroqService()
    assert service.needs_search("погода в Алматы") == True
    assert service.needs_search("привет") == False


def test_pick_model_long_text():
    from services.groq_service import GroqService
    service = GroqService()
    long_text = "расскажи мне подробно о истории Казахстана начиная с древних времен"
    model = service.pick_model(long_text)
    assert model == service.model_smart


def test_system_prompt_contains_date():
    from services.groq_service import GroqService
    service = GroqService()
    prompt = service.get_system_prompt()
    assert "2026" in prompt


def test_search_cache():
    from services.search_service import set_cache, get_cached
    set_cache("test_query", [{"title": "Test"}])
    result = get_cached("test_query")
    assert result is not None
    assert result[0]["title"] == "Test"


def test_format_results_empty():
    from services.search_service import format_results
    result = format_results([])
    assert len(result) > 0


def test_format_results_with_data():
    from services.search_service import format_results
    data = [{"title": "Test", "url": "https://test.com", "snippet": "Test snippet"}]
    result = format_results(data)
    assert "Test" in result


def test_rate_limiter_allows():
    from utils.rate_limiter import RateLimiter
    limiter = RateLimiter()
    allowed, msg = limiter.is_allowed(1001, 1001)
    assert allowed == True


def test_rate_limiter_message():
    from utils.rate_limiter import RateLimiter
    limiter = RateLimiter()
    limiter.USER_LIMIT = 1
    limiter.is_allowed(2001, 2001)
    allowed, msg = limiter.is_allowed(2001, 2001)
    assert allowed == False
    assert len(msg) > 0


def test_get_logger():
    from utils.logger import get_logger
    logger = get_logger("test")
    assert logger is not None


def test_get_request_logger():
    from utils.logger import get_request_logger
    logger = get_request_logger("test", user_id=123)
    assert logger is not None


@pytest.mark.asyncio
async def test_handle_text_message():
    from handlers.chat import handle_text_message
    message = make_message("Привет")
    with patch("services.storage.storage.save_user", new_callable=AsyncMock), \
         patch("services.storage.storage.get_chat_history", new_callable=AsyncMock, return_value=[]), \
         patch("services.storage.storage.save_message", new_callable=AsyncMock), \
         patch("services.groq_service.groq_service.get_chat_response", new_callable=AsyncMock, return_value="Привет!"):
        await handle_text_message(message)
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_handle_text_message_private():
    from handlers.chat import handle_text_message
    from handlers.common import private_users
    message = make_message("Привет", user_id=999)
    private_users.add(999)
    with patch("services.storage.storage.save_user", new_callable=AsyncMock), \
         patch("services.storage.storage.get_chat_history", new_callable=AsyncMock, return_value=[]), \
         patch("services.storage.storage.save_message", new_callable=AsyncMock), \
         patch("services.ollama_service.get_ollama_response", new_callable=AsyncMock, return_value="Ollama жауап"):
        await handle_text_message(message)
    message.answer.assert_called_once()
    private_users.discard(999)


@pytest.mark.asyncio
async def test_storage_save_user():
    from services.storage import Storage
    storage = Storage()
    storage.conn = MagicMock()
    cursor = MagicMock()
    storage.conn.cursor.return_value.__enter__ = MagicMock(return_value=cursor)
    storage.conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    await storage.save_user("testuser", "Test User", user_id=123)
    cursor.execute.assert_called_once()


@pytest.mark.asyncio
async def test_storage_save_message():
    from services.storage import Storage
    storage = Storage()
    storage.conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchone.return_value = (1,)
    storage.conn.cursor.return_value.__enter__ = MagicMock(return_value=cursor)
    storage.conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    await storage.save_message("testuser", "Hello", "Hi!", user_id=123)
    assert cursor.execute.called


@pytest.mark.asyncio
async def test_storage_get_chat_history_empty():
    from services.storage import Storage
    storage = Storage()
    storage.conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchall.return_value = []
    storage.conn.cursor.return_value.__enter__ = MagicMock(return_value=cursor)
    storage.conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    result = await storage.get_chat_history("testuser")
    assert result == []


@pytest.mark.asyncio
async def test_handle_voice_message_no_text():
    from handlers.chat import handle_voice_message
    message = make_message("")
    message.voice = MagicMock()
    message.voice.file_id = "test_file_id"
    bot = AsyncMock()
    bot.get_file = AsyncMock(return_value=MagicMock(file_path="test/path.ogg"))
    bot.download_file = AsyncMock()
    with patch("services.storage.storage.save_user", new_callable=AsyncMock), \
         patch("services.groq_service.groq_service.transcribe_audio", new_callable=AsyncMock, return_value={"text": "", "language": "ru"}):
        await handle_voice_message(message, bot)
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_handle_voice_message_with_text():
    from handlers.chat import handle_voice_message
    message = make_message("")
    message.voice = MagicMock()
    message.voice.file_id = "test_file_id"
    bot = AsyncMock()
    bot.get_file = AsyncMock(return_value=MagicMock(file_path="test/path.ogg"))
    bot.download_file = AsyncMock()
    with patch("services.storage.storage.save_user", new_callable=AsyncMock), \
         patch("services.storage.storage.get_chat_history", new_callable=AsyncMock, return_value=[]), \
         patch("services.storage.storage.save_message", new_callable=AsyncMock), \
         patch("services.groq_service.groq_service.transcribe_audio", new_callable=AsyncMock, return_value={"text": "Привет", "language": "ru"}), \
         patch("services.groq_service.groq_service.get_chat_response", new_callable=AsyncMock, return_value="Привет!"):
        await handle_voice_message(message, bot)
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_dbexport_command():
    from handlers.common import cmd_dbexport
    message = make_message("/dbexport")
    with patch("handlers.common.export_to_csv", new_callable=AsyncMock) as mock:
        mock.return_value = "id,user_id\n1,123"
        await cmd_dbexport(message)
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_dbusers_command():
    from handlers.common import cmd_dbusers
    message = make_message("/dbusers")
    with patch("handlers.common.query_users", new_callable=AsyncMock) as mock:
        mock.return_value = "Пайдаланушылар: 1"
        await cmd_dbusers(message)
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_benchmark_command():
    from handlers.common import cmd_benchmark
    message = make_message("/benchmark")
    with patch("services.ollama_service.get_ollama_response", new_callable=AsyncMock, return_value="ok"), \
         patch("services.groq_service.groq_service.get_response", new_callable=AsyncMock, return_value="ok"):
        await cmd_benchmark(message)
    message.answer.assert_called()


@pytest.mark.asyncio
async def test_handle_photo_message():
    from handlers.chat import handle_photo
    message = make_message("")
    message.photo = [MagicMock(file_id="test_photo_id")]
    message.caption = "Суретте не бар?"
    message.answer_photo = AsyncMock()
    bot = AsyncMock()
    bot.get_file = AsyncMock(return_value=MagicMock(file_path="test/path.jpg"))
    bot.download_file = AsyncMock()

    with patch("services.storage.storage.save_user", new_callable=AsyncMock), \
         patch("services.storage.storage.save_message", new_callable=AsyncMock), \
         patch("builtins.open", MagicMock(return_value=MagicMock(
             __enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=b"fakeimage"))),
             __exit__=MagicMock(return_value=False)
         ))), \
         patch("os.path.exists", return_value=False), \
         patch("groq.AsyncGroq") as mock_groq:
        mock_client = AsyncMock()
        mock_groq.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            return_value=MagicMock(choices=[MagicMock(message=MagicMock(content="Бұл мысық!"))])
        )
        await handle_photo(message, bot)
    message.answer.assert_called()


@pytest.mark.asyncio
async def test_handle_photo_exception():
    from handlers.chat import handle_photo
    message = make_message("")
    message.photo = [MagicMock(file_id="test_photo_id")]
    message.caption = None
    bot = AsyncMock()
    bot.get_file = AsyncMock(side_effect=Exception("Network error"))

    with patch("services.storage.storage.save_user", new_callable=AsyncMock):
        await handle_photo(message, bot)
    message.answer.assert_called()


@pytest.mark.asyncio
async def test_handle_voice_message_exception():
    from handlers.chat import handle_voice_message
    message = make_message("")
    message.voice = MagicMock()
    message.voice.file_id = "test_file_id"
    bot = AsyncMock()
    bot.get_file = AsyncMock(side_effect=Exception("Download error"))

    with patch("services.storage.storage.save_user", new_callable=AsyncMock):
        await handle_voice_message(message, bot)
    message.answer.assert_called()


@pytest.mark.asyncio
async def test_handle_text_no_username():
    from handlers.chat import handle_text_message
    message = make_message("Сәлем")
    message.from_user.username = None

    with patch("services.storage.storage.save_user", new_callable=AsyncMock), \
         patch("services.storage.storage.get_chat_history", new_callable=AsyncMock, return_value=[]), \
         patch("services.storage.storage.save_message", new_callable=AsyncMock), \
         patch("services.groq_service.groq_service.get_chat_response", new_callable=AsyncMock, return_value="Жауап"):
        await handle_text_message(message)
    message.answer.assert_called_once()