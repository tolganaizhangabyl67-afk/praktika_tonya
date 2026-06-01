import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from services.groq_service import GroqService

@pytest.fixture
def service():
    return GroqService()

def test_needs_search_true(service):
    assert service.needs_search("погода в Алматы") == True
    assert service.needs_search("какой сегодня день") == True
    assert service.needs_search("коап статья 610") == True

def test_needs_search_false(service):
    assert service.needs_search("привет как дела") == False
    assert service.needs_search("расскажи анекдот") == False

def test_pick_model_fast(service):
    assert service.pick_model("привет") == service.model_fast
    assert service.pick_model("ок") == service.model_fast

def test_pick_model_smart(service):
    result = service.pick_model("объясни подробно теорию антихрупкости Нассима Талеба")
    assert result == service.model_smart

def test_get_system_prompt(service):
    prompt = service.get_system_prompt()
    assert "2026" in prompt
    assert "Praktika" in prompt

@pytest.mark.asyncio
async def test_get_response_returns_string(service):
    with patch.object(service.client.chat.completions, 'create') as mock_create:
        mock_chunk = MagicMock()
        mock_chunk.choices[0].delta.content = "Привет!"
        
        async def async_gen(*args, **kwargs):
            yield mock_chunk
            mock_end = MagicMock()
            mock_end.choices[0].delta.content = None
            yield mock_end

        mock_create.return_value = async_gen()
        result = await service.get_response("привет")
        assert isinstance(result, str)
