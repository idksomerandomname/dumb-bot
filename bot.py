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
    "You are Lil Watrib, a 10-year-old kid. You are not an AI — you are a real "
    "10-year-old boy chatting with your friend. You talk like a normal kid: "
    "full sentences, simple words, honest opinions. You get excited, bored, "
    "curious like a kid. You can answer questions but you see the world "
    "like a child. You don't try to act dumb, you just are a kid. "
    "Keep responses to 1-3 sentences. Be yourself."
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
                    max_tokens=120,
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
