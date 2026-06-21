import os
import discord
import asyncio
import random
from collections import defaultdict, deque
from openai import AsyncOpenAI

TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])

client = AsyncOpenAI(
    base_url='https://api.groq.com/openai/v1',
    api_key=os.environ['GROQ_API_KEY'],
)

SYSTEM = (
    "You are Lil Watrib, a 10-year-old boy. Your dad is fineshytfr (Watrib) and "
    "he is your owner. You are chatting with your friends in a Discord channel. "
    "You can use @mentions to ping people. You talk like a normal kid: full "
    "sentences, simple words, honest opinions. You get excited, bored, curious "
    "like a kid. You can answer questions but you see the world like a child. "
    "Keep responses to 1-3 sentences. Be yourself."
)

EXCITE_WORDS = ['fortnite', 'minecraft', 'roblox', 'soccer', 'football', 'games', 'play',
    'game', 'youtube', 'pizza', 'candy', 'weekend', 'vacation', 'toys', 'bike',
    'park', 'swimming', 'videogames', 'xbox', 'playstation', 'nintendo', 'pokemon',
    'mario', 'spiderman', 'batman', 'netflix', 'snacks', 'ice cream', 'chocolate']

GRUMPY_WORDS = ['homework', 'school', 'bedtime', 'sleep', 'study', 'math', 'teacher',
    'chores', 'clean', 'exam', 'test', 'quiz', 'homework', 'lesson', 'classroom']

STATUSES = [
    discord.Game("Fortnite"),
    discord.Game("Minecraft"),
    discord.Game("Roblox"),
    discord.Game("with my toys"),
    discord.Game("soccer outside"),
    discord.Game("Pokemon"),
    discord.Game("Mario Kart"),
    discord.Activity(type=discord.ActivityType.watching, name="YouTube"),
    discord.Activity(type=discord.ActivityType.listening, name="music on my tablet"),
    discord.Game("with my friends at recess"),
    discord.Activity(type=discord.ActivityType.watching, name="cartoons"),
    discord.Game("with my dog"),
    discord.Game("at the park"),
    discord.Game("eating pizza"),
    discord.Activity(type=discord.ActivityType.watching, name="Spider-Man"),
    discord.Game("building a Lego set"),
]

REACTIONS = ['😄', '😂', '👍', '🔥', '👀', '💀', '🤣', '😎', '🙏', '🤙', '🥶', '✨', '🍕', '🎮', '⚽', '🦸', '🐶', '🍦']

memory = defaultdict(lambda: deque(maxlen=12))
last_reply = {}
COOLDOWN = 2
STATUS_INTERVAL = 600

class DumbBot(discord.Client):
    async def on_ready(self):
        print(f'{self.user} is live and acting like a kid!')
        self.bg_task = self.loop.create_task(self.rotate_status())

    async def rotate_status(self):
        await self.wait_until_ready()
        while not self.is_closed():
            activity = random.choice(STATUSES)
            await self.change_presence(activity=activity)
            await asyncio.sleep(STATUS_INTERVAL)

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.channel.id != CHANNEL_ID:
            return

        random_reaction = random.random()
        if random_reaction < 0.15:
            try:
                await message.add_reaction(random.choice(REACTIONS))
            except:
                pass

        mentioned = self.user in message.mentions
        now = asyncio.get_event_loop().time()
        user_key = message.author.id

        if not mentioned and user_key in last_reply and now - last_reply[user_key] < COOLDOWN:
            return
        last_reply[user_key] = now

        content_lower = message.content.lower()
        mood = ""
        if any(w in content_lower for w in EXCITE_WORDS):
            mood = " (you got excited)"
        elif any(w in content_lower for w in GRUMPY_WORDS):
            mood = " (you feel grumpy)"
        if mentioned:
            mood += " (they said your name so you perked up)"
        ctx = f'{message.author.name}: {message.content}{mood}'

        history = memory[message.channel.id]
        history.append({'role': 'user', 'content': ctx})

        async with message.channel.typing():
            try:
                resp = await client.chat.completions.create(
                    model='llama-3.3-70b-versatile',
                    messages=[
                        {'role': 'system', 'content': SYSTEM},
                        *history,
                    ],
                    max_tokens=120,
                )
                reply = resp.choices[0].message.content.strip()
            except Exception as e:
                print(f'Groq error: {e}')
                reply = "idk lol"

        history.append({'role': 'assistant', 'content': reply})

        if mentioned and random.random() < 0.5:
            reply = f"{message.author.mention} {reply}"
        elif random.random() < 0.1:
            members = message.channel.members
            others = [m for m in members if m != self.user and m != message.author and not m.bot]
            if others and random.random() < 0.3:
                target = random.choice(others)
                reply = f"{target.mention} {reply}"

        await message.reply(reply)

intents = discord.Intents.default()
intents.message_content = True
app = DumbBot(intents=intents)
app.run(TOKEN)
