from discord.ext import commands
import discord
import os
from dotenv import load_dotenv
from gears.useful import load_cogs
import json
from motor.motor_asyncio import AsyncIOMotorClient

config = json.load(open("config.json"))

load_dotenv()

prefix = config.get("Bot").get("Prefix")


async def get_prefix(bot, message):
    """Gets the prefix from built cache, if a guild isn't found (Direct Messages) assumes prefix is the below"""
    if message.guild is None:
        return bot.prefix
    else:
        return bot.prefix_cache[str(message.guild.id)]


intents = discord.Intents(
    bans=True,
    dm_messages=True,
    dm_reactions=True,
    dm_typing=True,
    emojis=True,
    guild_messages=True,
    guild_reactions=True,
    guild_typing=True,
    guilds=True,
    integrations=True,
    invites=True,
    members=True,
    messages=True,
    presences=True,
    reactions=True,
    typing=True,
    voice_states=True,
    webhooks=True,
)

bot = commands.Bot(
    command_prefix="s",
    intents=intents,
    description="The coolest bot ever",
    Intents=discord.Intents.all(),
)

bot.config = config
print("Loaded Bot Config")
bot.prefix = prefix

mongo_uri = (
    config.get("Mongo")
    .get("URL")
    .replace("<Username>", config.get("Mongo").get("User"))
    .replace("<Password>", os.getenv("Mongo_Pass"))
)

bot.mongo = AsyncIOMotorClient(mongo_uri)
print("Loaded Bot DB")

load_cogs(bot, os.listdir("src/cogs"))


@bot.event
async def on_ready():
    """On ready tell us"""
    print(f"Bot {bot.user} logged in.")


@bot.event
async def on_cache_prefixes():
    """Cache Prefixes"""
    prefix_db = bot.mongo["Prefixes"]

    for server in prefix_db:
        pass


bot.dispatch("cache_prefixes")

bot.run(os.getenv("Bot_Token"))
