import asyncio, os, httpx
from datetime import datetime
from openai import AsyncOpenAI

async def main():
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    today = datetime.now().strftime("%d.%m.%Y")
    prompt = f"Сегодня {today}. Придумай 5 идей для контента (Reels/посты) на тему недвижимости СПб и ипотеки. Для каждой: формат, тема, описание. Начни с '💡 Идеи для контента:'"
    response = await client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}], max_tokens=2000)
    async with httpx.AsyncClient() as http:
        await http.post(f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage", json={"chat_id": os.getenv('CHAT_ID'), "text": response.choices[0].message.content})

if __name__ == "__main__":
    asyncio.run(main())
