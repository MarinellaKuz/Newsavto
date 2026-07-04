import asyncio, os, httpx
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
        for item in root.findall(".//item")[:10]:
            title = item.find("title")
            desc = item.find("description")
            date = item.find("pubDate")
            items.append(f"{date.text if date is not None else ''}: {title.text if title is not None else ''}")
    except:
        pass
    return items

async def main():
    feeds = [
        "https://habr.com/ru/rss/hub/artificial_intelligence/all/?fl=ru",
        "https://techcrunch.com/category/artificial-intelligence/feed/"
    ]
    all_news = []
    for url in feeds:
        xml = await get_rss(url)
        all_news.extend(await parse_rss(xml))
    
    news_text = "\n".join(all_news[:15])
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"Вот свежие новости ИИ:\n{news_text}\n\nВыбери 10 важных, переведи на русский. Формат:\n📌 Заголовок\n💡 Суть\n\nНачни: 🤖 Новости ИИ:"
    
    response = await client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=3000)
    async with httpx.AsyncClient() as http:
        await http.post(f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage", json={"chat_id": os.getenv("CHAT_ID"), "text": response.choices[0].message.content})

if __name__ == "__main__":
    asyncio.run(main())
