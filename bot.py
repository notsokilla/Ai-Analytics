import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NEURAL_NETWORK_API_KEY = os.getenv("NEURAL_API_KEY")
NEURAL_NETWORK_URL = os.getenv("NEURAL_BASE_URL", "https://openrouter.ai/api/v1")
NEURAL_MODEL = os.getenv("NEURAL_MODEL", "meta-llama/llama-3.1-70b-instruct")

# Инициализация
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

client = AsyncOpenAI(
    api_key=NEURAL_NETWORK_API_KEY,
    base_url=NEURAL_NETWORK_URL

)

# ================= ПРОМПТ (ЗАДАЧА ДЛЯ НЕЙРОСЕТИ) =================
SYSTEM_INSTRUCTION = """
Ты — игровой бот-ассистент.
Твоя задача: отвечать на вопросы про игры, билды, стратегии и киберспорт.
Ты подключен к нейросети. Ты должен генерировать текст.
Главное — отвечай в теме игр. Не используй любое форматирование.

"""

# ================= ФУНКЦИЯ ВЫЗОВА НЕЙРОСЕТИ =================
async def ask_neural_network(user_text: str) -> str:
    try:
        response = await client.chat.completions.create(
            model=NEURAL_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": user_text}
            ],
            temperature=0.0, # Высокая креативность
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Ошибка связи с нейросетью: {str(e)}"

# ================= ОБРАБОТЧИКИ TELEGRAM =================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🤖 БОТ ЗАПУЩЕН.\n"
        "✅ НЕЙРОСЕТЬ ПОДКЛЮЧЕНА.\n"
        "Пиши любой вопрос по играм (билды, матчи, стратегии)."
    )

@dp.message()
async def handle_user_message(message: types.Message):
    waiting_msg = await message.answer("🔄 Нейросеть анализирует запрос...")

    ai_response = await ask_neural_network(message.text)

    await waiting_msg.delete()
    await message.answer(ai_response)

# ================= ЗАПУСК =================
async def main():
    logging.basicConfig(level=logging.INFO)
    print("✅ БОТ ЗАПУЩЕН И ЖДЕТ СОБЫТИЙ...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())