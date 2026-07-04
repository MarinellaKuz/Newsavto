import asyncio, os, httpx
from datetime import datetime
from openai import AsyncOpenAI

async def search_news(query):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30
        )
        return response.text[:12000]

async def main():
    queries = [
        "ключевая ставка ЦБ ипотека июль 2024",
        "льготная ипотека семейная IT изменения",
        "недвижимость Санкт-Петербург цены июль 2024",
        "Сбербанк ВТБ ипотека ставки условия"
    ]
    
    all_results = ""
    for q in queries:
        all_results += await search_news(q) + "\n\n"
    
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    today = datetime.now().strftime("%d.%m.%Y")
    
    prompt = f"""Сегодня {today}. На основе поиска составь ДАЙДЖЕСТ для риелтора СПб.

Данные из поиска:
{all_results[:30000]}

Напиши ТОЛЬКО то, что нашёл в поиске (не выдумывай цифры):

📊 **ИПОТЕКА**
- Ключевая ставка ЦБ (если есть)
- Ставки банков (Сбер, ВТБ, Альфа)
- Изменения в льготных программах

🏠 **РЫНОК СПБ**
- Цены (если есть данные)
- Что происходит на рынке

📰 **НОВОСТИ НЕДЕЛИ**
- 3-5 конкретных новостей с датами

💬 **ДЛЯ РАЗГОВОРА С КЛИЕНТАМИ**
- 2-3 актуальные темы

Начни: "🏠 Дайджест недвижимости на {today}:"
Если данных мало — честно напиши что нашёл.
НЕ ВЫДУМЫВАЙ цифры и факты!"""

    response = await client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=3000)
    
    async with httpx.AsyncClient() as http:
        text = response.choices[0].message.content
        for i in range(0, len(text), 4000):
            await http.post(f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage", 
                          json={"chat_id": os.getenv("CHAT_ID"), "text": text[i:i+4000]})

if __name__ == "__main__":
    asyncio.run(main())
    
