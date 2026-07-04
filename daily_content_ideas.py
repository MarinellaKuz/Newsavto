import asyncio, os, httpx
from datetime import datetime
from openai import AsyncOpenAI
import xml.etree.ElementTree as ET

async def get_rss(url):
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            return r.text
        except:
            return ""

async def parse_rss(xml_text):
    items = []
    try:
        root = ET.fromstring(xml_text)
        for item in root.findall(".//item")[:5]:
            title = item.find("title")
            items.append(title.text if title is not None else "")
    except:
        pass
    return items

async def main():
    feeds = [
        "https://realty.rbc.ru/rss/",
        "https://www.fontanka.ru/realty.rss"
    ]
    
    news = []
    for url in feeds:
        xml = await get_rss(url)
        items = await parse_rss(xml)
        news.extend(items)
    
    news_text = "\n".join([f"• {n}" for n in news[:10]])
    
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    today = datetime.now().strftime("%d.%m.%Y")
    weekday = ["Понедельник","Вторник","Среда","Четверг","Пятница","Суббота","Воскресенье"][datetime.now().weekday()]
    
    prompt = f"""Ты SMM для риелтора СПб. Сегодня {weekday}, {today}.

Свежие новости недвижимости:
{news_text}

Придумай 5 идей для Reels/постов, ПРИВЯЗАННЫХ к этим новостям:

Для каждой:
📱 **Формат:** Reels 30сек / Карусель
🎯 **Тема:** конкретная, привязанная к новости
🎬 **Хук:** первые 3 секунды (цепляющая фраза)
📝 **Сценарий:** что говорить (4-5 пунктов)

Начни: "💡 Идеи на {weekday}, {today}:"
Закончи: "Выбери и снимай! 🎬"
"""

    response = await client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=2500)
    
    async with httpx.AsyncClient() as http:
        await http.post(f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage", 
                      json={"chat_id": os.getenv("CHAT_ID"), "text": response.choices[0].message.content})

if __name__ == "__main__":
    asyncio.run(main())
    
