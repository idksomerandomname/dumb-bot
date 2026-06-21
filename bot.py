import os
import discord
from openai import OpenAI

TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])

client = OpenAI(
    base_url='https://openrouter.ai/api/v1',
    api_key=os.environ['OPENROUTER_KEY'],
)

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
                resp = client.chat.completions.create(
                    model='meta-llama/llama-3.2-3b-instruct:free',
                    messages=[
                        {'role': 'system', 'content': SYSTEM},
                        {'role': 'user', 'content': message.content},
                    ],
                )
                reply = resp.choices[0].message.content.strip()
            except Exception as e:
                print(f'OpenRouter error: {e}')
                reply = "idk lol"

        await message.reply(reply)

intents = discord.Intents.default()
intents.message_content = True
app = DumbBot(intents=intents)
app.run(TOKEN)
