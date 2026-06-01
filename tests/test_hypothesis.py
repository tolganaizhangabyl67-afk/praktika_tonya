import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from services.groq_service import GroqService
from services.search_service import format_results
from utils.rate_limiter import RateLimiter

service = GroqService()

# Тест 1: needs_search никогда не падает на любой строке
@given(st.text(max_size=4096))
def test_needs_search_never_crashes(text):
    result = service.needs_search(text)
    assert isinstance(result, bool)

# Тест 2: pick_model всегда возвращает одну из двух моделей
@given(st.text(max_size=4096))
def test_pick_model_always_valid(text):
    result = service.pick_model(text)
    assert result in [service.model_fast, service.model_smart]

# Тест 3: format_results никогда не падает
@given(st.lists(
    st.fixed_dictionaries({
        "title": st.text(max_size=200),
        "url": st.text(max_size=200),
        "snippet": st.text(max_size=500)
    }),
    max_size=10
))
def test_format_results_never_crashes(results):
    output = format_results(results)
    assert isinstance(output, str)

# Тест 4: rate limiter никогда не падает
@given(st.integers(min_value=1, max_value=999999), st.integers(min_value=1, max_value=999999))
def test_rate_limiter_never_crashes(user_id, chat_id):
    limiter = RateLimiter()
    allowed, reason = limiter.is_allowed(user_id, chat_id)
    assert isinstance(allowed, bool)
    assert isinstance(reason, str)

# Тест 5: длинные строки не вызывают ошибок
@given(st.text(min_size=100, max_size=4096))
def test_long_messages_handled(text):
    result = service.needs_search(text)
    assert result is not None
