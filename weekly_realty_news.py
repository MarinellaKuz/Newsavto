import asyncio, os, httpx
from openai import AsyncOpenAI

async def search_news(query):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query, "df": "w"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30
        )
        return response.text[:15000]

async def main():
    searches = [
        "ипотека ставки ЦБ РФ 2024",
        "недвижимость Санкт-Петербург цены новости",
        "льготная ипотека семейная IT новости"
    ]
    
    all_results = ""
    for q in searches:
        all_results += await search_news(q) + "\n\n"
    
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"""На основе этих результатов поиска составь еженедельный дайджест по недвижимости СПб.

Результаты поиска:
{all_results[:20000]}

Включи разделы:
1. 📊 ИПОТЕКА — ставки, изменения, льготные программы
2. 🏠 РЫНОК СПБ — цены, динамика, тренды
3. 📰 ГЛАВНЫЕ НОВОСТИ — 3-5 важных новостей недели
4. 💬 О ЧЁМ ГОВОРИТЬ С КЛИЕНТАМИ — актуальные темы

Начни с "🏠 Дайджест недвижимости:"
Закончи "Успешной недели! 💪"
Пиши конкретно, с цифрами."""

    response = await client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=3000)
    
    async with httpx.AsyncClient() as http:
        text = response.choices[0].message.content
        for i in range(0, len(text), 4000):
            await http.post(f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage", 
                          json={"chat_id": os.getenv("CHAT_ID"), "text": text[i:i+4000]})

if __name__ == "__main__":
    asyncio.run(main())
