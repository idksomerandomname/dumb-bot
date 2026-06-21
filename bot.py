import os
import discord
import asyncio
from openai import AsyncOpenAI

TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])

client = AsyncOpenAI(
    base_url='https://api.groq.com/openai/v1',
    api_key=os.environ['GROQ_API_KEY'],
)

SYSTEM = (
    "You are a 10-year-old kid named Lil Watrib. You are chill, dumb, and friendly. "
    "You respond to messages like a child would — short replies, simple words, "
    "sometimes misspelled. You say things like idk, bro, nice, cool, "
    "same, fr, bet, lol, hmm, ok, yeah, nah. You don't "
    "understand complex topics. You're just a chill dumb kid vibing. "
    "Keep responses very short (1-5 words). Never be mean."
)

last_reply = 0
COOLDOWN = 2

class DumbBot(discord.Client):
    async def on_ready(self):
        print(f'{self.user} is live and acting dumb!')

    async def on_message(self, message):
        global last_reply
        if message.author == self.user:
            return
        if message.channel.id != CHANNEL_ID:
            return

        now = asyncio.get_event_loop().time()
        if now - last_reply < COOLDOWN:
            return
        last_reply = now

        async with message.channel.typing():
            try:
                resp = await client.chat.completions.create(
                    model='llama-3.3-70b-versatile',
                    messages=[
                        {'role': 'system', 'content': SYSTEM},
                        {'role': 'user', 'content': message.content},
                    ],
                    max_tokens=50,
                )
                reply = resp.choices[0].message.content.strip()
            except Exception as e:
                print(f'Groq error: {e}')
                reply = "idk lol"

        await message.reply(reply)

intents = discord.Intents.default()
intents.message_content = True
app = DumbBot(intents=intents)
app.run(TOKEN)
