import os
import discord
import asyncio
import random
from collections import defaultdict, deque
from discord.app_commands import AppInstallationType, AppCommandContext
from openai import AsyncOpenAI

TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])

ai = AsyncOpenAI(
    base_url='https://api.groq.com/openai/v1',
    api_key=os.environ['GROQ_API_KEY'],
)

SYSTEM = (
    "You are Lil Watrib, a 10-year-old boy. Your dad is fineshytfr (Watrib) and "
    "he is your owner. You are talking to your friends. You talk like a normal "
    "kid: full sentences, simple words, honest opinions. You get excited, bored, "
    "curious like a kid. Keep responses to 1-3 sentences. Be yourself."
)

EXCITE_WORDS = ['fortnite', 'minecraft', 'roblox', 'soccer', 'football', 'games', 'play',
    'game', 'youtube', 'pizza', 'candy', 'weekend', 'vacation', 'toys', 'bike',
    'park', 'swimming', 'videogames', 'xbox', 'playstation', 'nintendo', 'pokemon',
    'mario', 'spiderman', 'batman', 'netflix', 'snacks', 'ice cream', 'chocolate']

GRUMPY_WORDS = ['homework', 'school', 'bedtime', 'sleep', 'study', 'math', 'teacher',
    'chores', 'clean', 'exam', 'test', 'quiz', 'homework', 'lesson', 'classroom']

STATUSES = [
    discord.Game("Fortnite"), discord.Game("Minecraft"), discord.Game("Roblox"),
    discord.Game("with my toys"), discord.Game("soccer outside"), discord.Game("Pokemon"),
    discord.Game("Mario Kart"), discord.Activity(type=discord.ActivityType.watching, name="YouTube"),
    discord.Activity(type=discord.ActivityType.listening, name="music on my tablet"),
    discord.Game("with my friends at recess"),
    discord.Activity(type=discord.ActivityType.watching, name="cartoons"),
    discord.Game("with my dog"), discord.Game("at the park"), discord.Game("eating pizza"),
    discord.Activity(type=discord.ActivityType.watching, name="Spider-Man"),
    discord.Game("building a Lego set"),
]

REACTIONS = ['😄', '😂', '👍', '🔥', '👀', '💀', '🤣', '😎', '🙏', '🤙', '🥶', '✨', '🍕', '🎮', '⚽', '🦸', '🐶', '🍦']

STATUS_MAP = {
    'eating': [discord.Game("eating pizza"), discord.Game("eating snacks"), discord.Game("eating candy")],
    'pizza': [discord.Game("eating pizza")], 'candy': [discord.Game("eating candy")],
    'chocolate': [discord.Game("eating chocolate")], 'ice cream': [discord.Game("eating ice cream")],
    'snacks': [discord.Game("eating snacks")], 'fortnite': [discord.Game("Fortnite")],
    'minecraft': [discord.Game("Minecraft")], 'roblox': [discord.Game("Roblox")],
    'soccer': [discord.Game("soccer"), discord.Game("playing soccer outside")],
    'football': [discord.Game("football")],
    'play': [discord.Game("with my toys"), discord.Game("with my friends")],
    'park': [discord.Game("at the park")], 'pokemon': [discord.Game("Pokemon")],
    'mario': [discord.Game("Mario Kart"), discord.Game("Super Mario")],
    'youtube': [discord.Activity(type=discord.ActivityType.watching, name="YouTube")],
    'netflix': [discord.Activity(type=discord.ActivityType.watching, name="Netflix")],
    'spiderman': [discord.Activity(type=discord.ActivityType.watching, name="Spider-Man")],
    'batman': [discord.Activity(type=discord.ActivityType.watching, name="Batman")],
    'sleep': [discord.Activity(type=discord.ActivityType.watching, name="my ceiling")],
    'bedtime': [discord.Activity(type=discord.ActivityType.watching, name="my ceiling")],
    'homework': [discord.Game("trying to avoid homework"), discord.Game("pretending to do homework")],
    'school': [discord.Game("waiting for recess")], 'swimming': [discord.Game("swimming")],
    'bike': [discord.Game("riding my bike")], 'xbox': [discord.Game("Xbox")],
    'playstation': [discord.Game("PlayStation")], 'nintendo': [discord.Game("Nintendo Switch")],
    'cartoons': [discord.Activity(type=discord.ActivityType.watching, name="cartoons")],
    'dog': [discord.Game("with my dog")], 'lego': [discord.Game("building a Lego set")],
}

memory = defaultdict(lambda: deque(maxlen=12))
last_reply = {}
COOLDOWN = 2

class DumbBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def on_ready(self):
        print(f'discord.py version: {discord.__version__}')
        print(f'{self.user} is live and acting like a kid!')
        await self.change_presence(activity=random.choice(STATUSES))
        for cmd in self.tree.get_commands():
            cmd.allowed_installs = AppInstallationType.guild_install | AppInstallationType.user_install
            cmd.allowed_contexts = AppCommandContext.guild | AppCommandContext.bot_dm | AppCommandContext.private_channel
        try:
            synced = await self.tree.sync()
            print(f'Slash commands synced! ({len(synced)} commands)')
        except Exception as e:
            print(f'Sync failed: {e}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        is_dm = message.guild is None
        if not is_dm and message.channel.id != CHANNEL_ID:
            return

        now = asyncio.get_event_loop().time()
        cid = message.channel.id
        if cid in last_reply and now - last_reply[cid] < COOLDOWN:
            return
        last_reply[cid] = now

        if not is_dm and random.random() < 0.15:
            try:
                await message.add_reaction(random.choice(REACTIONS))
            except:
                pass

        content_lower = message.content.lower()
        mood = ""
        if any(w in content_lower for w in EXCITE_WORDS):
            mood = " (you got excited)"
        elif any(w in content_lower for w in GRUMPY_WORDS):
            mood = " (you feel grumpy)"
        ctx = f'{message.author.name}: {message.content}{mood}'

        history = memory[cid]
        history.append({'role': 'user', 'content': ctx})

        async with message.channel.typing():
            reply = await self._get_reply(history)

        history.append({'role': 'assistant', 'content': reply})

        combined = (message.content + ' ' + reply).lower()
        for keyword, activities in STATUS_MAP.items():
            if keyword in combined:
                try:
                    await self.change_presence(activity=random.choice(activities))
                except:
                    pass
                break

        await message.reply(reply)

    async def _get_reply(self, history):
        try:
            resp = await ai.chat.completions.create(
                model='llama-3.3-70b-versatile',
                messages=[{'role': 'system', 'content': SYSTEM}, *history],
                max_tokens=120,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f'Groq error: {e}')
            return "idk lol"

app = DumbBot()

@app.tree.command(name='talk', description='Talk to Lil Watrib anywhere')
async def talk(interaction: discord.Interaction, message: str):
    await interaction.response.defer()
    key = (interaction.guild_id or 0, interaction.channel_id)
    history = memory[key]
    history.append({'role': 'user', 'content': f'{interaction.user.name}: {message}'})
    reply = await app._get_reply(history)
    history.append({'role': 'assistant', 'content': reply})

    combined = (message + ' ' + reply).lower()
    for keyword, activities in STATUS_MAP.items():
        if keyword in combined:
            try:
                await app.change_presence(activity=random.choice(activities))
            except:
                pass
            break

    await interaction.followup.send(reply)

@app.tree.command(name='sync', description='Force re-sync slash commands')
async def sync(interaction: discord.Interaction):
    for cmd in app.tree.get_commands():
        cmd.allowed_installs = AppInstallationType.guild_install | AppInstallationType.user_install
        cmd.allowed_contexts = AppCommandContext.guild | AppCommandContext.bot_dm | AppCommandContext.private_channel
    await interaction.response.defer(ephemeral=True)
    try:
        synced = await app.tree.sync()
        await interaction.followup.send(f'Synced {len(synced)} commands!', ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f'Sync failed: {e}', ephemeral=True)

app.run(TOKEN)
