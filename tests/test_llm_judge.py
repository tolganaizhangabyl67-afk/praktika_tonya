import pytest
import asyncio
from groq import AsyncGroq
import config

# 10 эталонных вопросов с правильными ответами
BENCHMARK = [
    {"question": "Кто такой Нассим Талеб?", "expected": "писатель, трейдер, философ, антихрупкость"},
    {"question": "Что такое антихрупкость?", "expected": "система становится сильнее от стрессов и потрясений"},
    {"question": "Столица Казахстана?", "expected": "Астана"},
    {"question": "Кто такой Ницше?", "expected": "немецкий философ, воля к власти, сверхчеловек"},
    {"question": "Что такое MCP?", "expected": "Model Context Protocol, протокол для инструментов ИИ"},
    {"question": "Кто такой Аль-Фараби?", "expected": "исламский философ, второй учитель, аль-Фараби"},
    {"question": "Что такое черный лебедь по Талебу?", "expected": "непредсказуемое событие с большими последствиями"},
    {"question": "Язык программирования Python создал?", "expected": "Гвидо ван Россум"},
    {"question": "Что такое Groq?", "expected": "быстрый AI inference, LPU"},
    {"question": "Что такое aiogram?", "expected": "библиотека для Telegram ботов на Python"},
]

async def get_bot_answer(question: str) -> str:
    """Получаем ответ от основной модели"""
    client = AsyncGroq(api_key=config.GROQ_API_KEY)
    response = await client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[
            {"role": "system", "content": "Ты — ИИ-ассистент Praktika. Отвечаешь чётко, без воды."},
            {"role": "user", "content": question}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content

async def judge_answer(question: str, answer: str, expected: str) -> int:
    """LLM оценивает ответ по шкале 1-10"""
    client = AsyncGroq(api_key=config.GROQ_API_KEY)
    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты — строгий оценщик качества ответов ИИ. "
                    "Оцени ответ по шкале от 1 до 10. "
                    "Отвечай ТОЛЬКО цифрой от 1 до 10, ничего больше."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Вопрос: {question}\n"
                    f"Ожидаемые ключевые слова: {expected}\n"
                    f"Ответ модели: {answer}\n\n"
                    f"Оцени точность и релевантность ответа (1-10):"
                )
            }
        ],
        temperature=0
    )
    try:
        score = int(response.choices[0].message.content.strip())
        return min(max(score, 1), 10)
    except:
        return 5

@pytest.mark.asyncio
async def test_llm_judge():
    scores = []
    print("\n\n=== LLM-as-a-Judge результаты ===")
    
    for item in BENCHMARK:
        answer = await get_bot_answer(item["question"])
        score = await judge_answer(item["question"], answer, item["expected"])
        scores.append(score)
        print(f"Q: {item['question'][:50]}")
        print(f"A: {answer[:100]}")
        print(f"Оценка: {score}/10\n")
    
    avg = sum(scores) / len(scores)
    print(f"Средняя оценка: {avg:.1f}/10")
    print(f"Минимум: {min(scores)}/10")
    print(f"Максимум: {max(scores)}/10")
    
    # Средняя оценка должна быть не ниже 6
    assert avg >= 6, f"Средняя оценка {avg:.1f} ниже порога 6.0!"
    print(f"\n✅ Тест пройден! Средняя оценка: {avg:.1f}/10")
