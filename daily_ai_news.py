import asyncio, os, httpx
from openai import AsyncOpenAI

async def search_news(query):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query, "df": "d"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30
        )
        return response.text[:15000]

async def main():
    search_results = await search_news("AI artificial intelligence news today 2024")
    
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"""На основе этих результатов поиска составь Топ-10 свежих новостей из мира ИИ.

Результаты поиска:
{search_results}

Для каждой новости укажи:
1. 📌 Заголовок
2. 💡 Суть (2-3 предложения)
3. 🎯 Почему важно

Начни с "🤖 Доброе утро! Топ-10 новостей ИИ:"
Закончи "Хорошего дня! 🚀"
Если новостей меньше 10 - напиши сколько нашёл."""

    response = await client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=3000)
    
    async with httpx.AsyncClient() as http:
        text = response.choices[0].message.content
        for i in range(0, len(text), 4000):
            await http.post(f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage", 
                          json={"chat_id": os.getenv("CHAT_ID"), "text": text[i:i+4000]})

if __name__ == "__main__":
    asyncio.run(main())
