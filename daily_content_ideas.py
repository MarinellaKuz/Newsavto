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
        return response.text[:10000]

async def main():
    trends = await search_news("риелтор блог инстаграм reels идеи недвижимость ипотека СПб")
    news = await search_news("ипотека новости Санкт-Петербург недвижимость цены")
    
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    today = datetime.now().strftime("%d.%m.%Y")
    weekday = ["Понедельник","Вторник","Среда","Четверг","Пятница","Суббота","Воскресенье"][datetime.now().weekday()]
    
    prompt = f"""Ты SMM-эксперт для риелтора из СПб. Сегодня {weekday}, {today}.

Актуальный контекст из поиска:
{trends[:8000]}
{news[:8000]}

Придумай 5 КОНКРЕТНЫХ идей для контента:

Для каждой идеи:
📱 **Формат:** Reels 30сек / Карусель / Stories
🎯 **Тема:** конкретная (не "про ипотеку", а "Почему в июле выгодно брать ипотеку")
📝 **Сценарий:** что говорить/показывать (3-4 предложения)
🎬 **Хук:** первая фраза чтобы зацепить

Темы должны быть:
- Привязаны к текущим новостям (ставки, цены, законы)
- Полезны покупателям/продавцам
- Не занудные, живые

Начни: "💡 Идеи на {weekday}:"
Закончи: "Выбери одну и снимай! 🎬"
"""

    response = await client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=2500)
    
    async with httpx.AsyncClient() as http:
        await http.post(f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage", 
                      json={"chat_id": os.getenv("CHAT_ID"), "text": response.choices[0].message.content})

if __name__ == "__main__":
    asyncio.run(main())
    
