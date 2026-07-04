#!/usr/bin/env python3
import asyncio
import os
import sys
from datetime import datetime

import httpx
from openai import AsyncOpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHAT_ID = os.getenv("CHAT_ID")


async def get_ai_news() -> str:
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    today = datetime.now().strftime("%d.%m.%Y")
    
    prompt = f"""Ты — AI-аналитик, эксперт по новостям искусственного интеллекта.

Сегодня {today}. Составь "Топ-10 новостей ИИ" — самые важные и интересные события.

Для каждой новости:
1. 📌 **Заголовок**
2. 💡 **Суть** — что произошло (2-3 предложения)
3. 🎯 **Почему важно** — влияние на индустрию (1 предложение)

Фокусируйся на:
- Новые модели (OpenAI, Anthropic, Google, Meta, Mistral, xAI)
- Прорывы в исследованиях
- Бизнес-новости (инвестиции, сделки)
- Новые инструменты и приложения

Формат: красивый текст для Telegram с эмодзи.
Начни: "🤖 Доброе утро! Топ-10 новостей ИИ:"
Закончи: "Хорошего дня! 🚀"
"""
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2500,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


async def send_telegram(text: str) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        max_len = 4000
        messages = [text[i:i+max_len] for i in range(0, len(text), max_len)]
        for msg in messages:
            try:
                response = await client.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
                if not response.is_success:
                    await client.post(url, json={"chat_id": CHAT_ID, "text": msg})
            except Exception as e:
                print(f"Ошибка: {e}")
                return False
    return True


async def main():
    print(f"🚀 Запуск: Новости ИИ — {datetime.now()}")
    if not all([BOT_TOKEN, OPENAI_API_KEY, CHAT_ID]):
        print("❌ Не заданы переменные!")
        sys.exit(1)
    news = await get_ai_news()
    print("✅ Новости сгенерированы")
    if await send_telegram(news):
        print("✅ Отправлено!")
    else:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
