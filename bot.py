import os
import discord
from dumb import MarkovChain

TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])

markov = MarkovChain()

class DumbBot(discord.Client):
    async def on_ready(self):
        print(f'{self.user} is live and learning!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.channel.id != CHANNEL_ID:
            return

        markov.learn(message.content)
        response = markov.generate()
        await message.reply(response)

intents = discord.Intents.default()
intents.message_content = True
client = DumbBot(intents=intents)
client.run(TOKEN)
