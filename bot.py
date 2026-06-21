import os
import discord
from google import genai

TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])
GEMINI_KEY = os.environ['GEMINI_API_KEY']

client = genai.Client(api_key=GEMINI_KEY)

SYSTEM_PROMPT = (
    "You are a 10-year-old kid named Lil Watrib. You are chill, dumb, and friendly. "
    "You respond to messages like a child would — short replies, simple words, "
    "sometimes misspelled. You say things like idk, bro, nice, cool, "
    "same, fr, bet, lol, hmm, ok, yeah, nah. You don't "
    "understand complex topics. You're just a chill dumb kid vibing. "
    "Keep responses very short (1-10 words). Never be mean."
)

class DumbBot(discord.Client):
    async def on_ready(self):
        print(f'{self.user} is live and acting dumb!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.channel.id != CHANNEL_ID:
            return

        async with message.channel.typing():
            try:
                resp = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=f"{SYSTEM_PROMPT}\n\nMessage: {message.content}\n\nReply:",
                )
                reply = resp.text.strip() if resp.text else "..."
            except Exception:
                reply = "..."

        await message.reply(reply)

intents = discord.Intents.default()
intents.message_content = True
app = DumbBot(intents=intents)
app.run(TOKEN)
