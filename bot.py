import os
import discord
import google.generativeai as genai
import logging

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])

genai.configure(api_key=os.environ['GEMINI_API_KEY'])

model = genai.GenerativeModel('gemini-1.5-flash')

SYSTEM = (
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
                resp = model.generate_content(f'{SYSTEM}\n\nMessage: {message.content}\n\nReply:')
                reply = resp.text.strip() if resp.text else "idk"
            except Exception as e:
                print(f'Gemini error: {e}')
                reply = "idk lol"

        await message.reply(reply)

intents = discord.Intents.default()
intents.message_content = True
app = DumbBot(intents=intents)
app.run(TOKEN)
