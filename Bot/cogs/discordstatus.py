import aiohttp
import asyncio
import discord
import discord.utils
from discord.ext import commands
from gears import style


class DiscordStatusClient:
    """A client for accessing info about discord status"""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = None
        self.api_url = "https://discordstatus.com/api/v2"


    async def fetch_summary(self) -> str:
        """
        Fetch a summary of the api's status
        """
        async with self.session.get(f"{self.api_url}/summary.json") as resp:
            if resp.status == 200:
                return await resp.json()
            raise DSException(f"{resp.status} {await resp.json()}")


class DSException(Exception):
    """
    Raised when we have an exception for DiscordStatusClass, shouldn't ever really happen
    """

    pass


class DiscordStatus(commands.Cog):
    """Cog Example Description"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self) -> None:
        """
        On cog load init
        """
        self.DSClient = DiscordStatusClient()
        await self.DSClient.async_init()

    async def cog_unload(self) -> None:
        """
        On cog load destroy previous client
        """
        await self.DSClient.close()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DiscordStatus(bot))
