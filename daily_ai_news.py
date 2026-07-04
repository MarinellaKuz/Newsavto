import asyncio, os, httpx
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
        "OpenAI GPT Claude Anthropic новости сегодня",
        "нейросети ИИ релиз обновление 2024",
        "Midjourney Sora Google Gemini новости"
    ]
    
    all_results = ""
    for q in queries:
        all_results += await search_news(q) + "\n"
    
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"""Из результатов поиска выбери ТОЛЬКО реальные свежие новости про ИИ.

{all_results[:25000]}

Напиши Топ-10 КОНКРЕТНЫХ новостей (не общие темы, а события):
- Какая компания что выпустила/анонсировала
- Какие обновления вышли
- Какие сделки/инвестиции произошли

Формат:
📌 **Заголовок**
💡 Что случилось (факты, даты, цифры)

Начни: "🤖 Новости ИИ:"
Если свежих новостей мало — напиши сколько нашёл, не выдумывай."""

    response = await client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=3000)
    
    async with httpx.AsyncClient() as http:
        text = response.choices[0].message.content
        for i in range(0, len(text), 4000):
            await http.post(f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage", 
                          json={"chat_id": os.getenv("CHAT_ID"), "text": text[i:i+4000]})

if __name__ == "__main__":
    asyncio.run(main())
