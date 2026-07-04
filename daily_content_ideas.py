import asyncio, os, httpx
from datetime import datetime
from openai import AsyncOpenAI

async def search_trends(query):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query, "df": "d"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30
        )
        return response.text[:10000]

async def main():
    trends = await search_trends("тренды reels недвижимость риелтор контент 2024")
    
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    today = datetime.now().strftime("%d.%m.%Y")
    
    prompt = f"""Сегодня {today}. На основе трендов придумай 5 идей для контента риелтора СПб.

Тренды из поиска:
{trends}

Для каждой идеи:
📱 Формат (Reels/пост/Stories)
🎯 Тема
📝 Что показать (2-3 предложения)
🔥 Почему зайдёт сейчас

Учитывай актуальные темы: ипотека, цены, лайфхаки покупателям.

Начни "💡 Идеи для контента на сегодня:"
Закончи "Выбери одну и сделай! ✨"
"""

    response = await client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=2000)
    
    async with httpx.AsyncClient() as http:
        await http.post(f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage", 
                      json={"chat_id": os.getenv("CHAT_ID"), "text": response.choices[0].message.content})

if __name__ == "__main__":
    asyncio.run(main())
