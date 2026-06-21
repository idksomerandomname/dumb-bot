import os
import discord
import asyncio
from google import genai

TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])

client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

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
                loop = asyncio.get_event_loop()
                resp = await loop.run_in_executor(
                    None,
                    lambda: client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=f'{SYSTEM}\n\nMessage: {message.content}\n\nReply:',
                    )
                )
                reply = resp.text.strip() if resp.text else "idk"
            except Exception as e:
                print(f'Gemini error: {e}')
                reply = "idk lol"

        await message.reply(reply)

intents = discord.Intents.default()
intents.message_content = True
app = DumbBot(intents=intents)
app.run(TOKEN)
