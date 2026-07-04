import asyncio, os, httpx
from datetime import datetime
from openai import AsyncOpenAI

async def main():
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    today = datetime.now().strftime("%d.%m.%Y")
    prompt = f"Сегодня {today}. Составь еженедельный дайджест по недвижимости СПб: ставки ипотеки ЦБ, льготные программы, цены на рынке, новости. Начни '🏠 Дайджест недвижимости:'"
    response = await client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}], max_tokens=2500)
    async with httpx.AsyncClient() as http:
        await http.post(f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage", json={"chat_id": os.getenv("CHAT_ID"), "text": response.choices[0].message.content})

if __name__ == "__main__":
    asyncio.run(main())
