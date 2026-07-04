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
        for item in root.findall(".//item")[:15]:
            title = item.find("title")
            desc = item.find("description")
            date = item.find("pubDate")
            items.append({
                "title": title.text if title is not None else "",
                "desc": desc.text[:300] if desc is not None and desc.text else "",
                "date": date.text if date is not None else ""
            })
    except:
        pass
    return items

async def main():
    feeds = [
        "https://realty.rbc.ru/rss/",
        "https://www.fontanka.ru/realty.rss",
        "https://www.vedomosti.ru/rss/rubric/realty"
    ]
    
    all_news = []
    for url in feeds:
        xml = await get_rss(url)
        items = await parse_rss(xml)
        all_news.extend(items)
    
    news_text = "\n".join([f"[{n['date']}] {n['title']}: {n['desc']}" for n in all_news[:25]])
    
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    today = datetime.now().strftime("%d.%m.%Y")
    
    prompt = f"""Сегодня {today}. Вот свежие новости недвижимости из RSS:

{news_text}

Составь дайджест для риелтора СПб:

📊 **ИПОТЕКА** — новости про ставки, программы, банки (из списка выше)

🏠 **РЫНОК** — что происходит с ценами, спросом (из списка)

📰 **ТОП-5 НОВОСТЕЙ НЕДЕЛИ** — самые важные из списка, с датами

💬 **О ЧЁМ ГОВОРИТЬ С КЛИЕНТАМИ** — 3 темы на основе новостей

Начни: "🏠 Дайджест недвижимости {today}:"
Закончи: "Успешной недели! 💪"
Пиши ТОЛЬКО на основе новостей из списка!"""

    response = await client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=3000)
    
    async with httpx.AsyncClient() as http:
        text = response.choices[0].message.content
        for i in range(0, len(text), 4000):
            await http.post(f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage", 
                          json={"chat_id": os.getenv("CHAT_ID"), "text": text[i:i+4000]})

if __name__ == "__main__":
    asyncio.run(main())
    
