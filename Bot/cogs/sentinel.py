import asqlite
import discord
import discord.utils
from discord.ext import commands
from gears import style
from detoxify import Detoxify


class Toxicity:
    """
    Toxicity info for easy access

    Attributes
    ----------
    toxicity: float
        Toxic level
    severe_toxicity: float

    """

    def __init__(self, prediction: dict) -> None:
        """
        Init

        Parameters
        ----------
        prediction: dict
            The prediction dict to build the Toxicity object off of
        """
        self.toxicity = round(prediction.get("toxicity"), 5) * 100
        self.severe_toxicity = round(prediction.get("severe_toxicity"), 5) * 100
        self.obscene = round(prediction.get("obscene"), 5) * 100
        self.identity_attack = round(prediction.get("identity_attack"), 5) * 100
        self.insult = round(prediction.get("insult"), 5) * 100
        self.threat = round(prediction.get("threat"), 5) * 100
        self.sexual_explicit = round(prediction.get("sexual_explicit"), 5) * 100
        self.average = (
            (
                self.toxicity
                + self.severe_toxicity
                + self.obscene
                + self.identity_attack
                + self.insult
                + self.threat
                + self.sexual_explicit
            )
            / 7
        ) * 100


class Config:
    """
    Config object
    """

    def __init__(
        self,
        channels: str,
        premium: bool,
        webhook: str,
        username: str,
        avatar: str,
        toxicity: int,
        severe_toxicity: int,
        obscene: int,
        identity_attack: int,
        insult: int,
        threat: int,
        sexual_explicit: int,
    ) -> None:
        """
        Init for config
        """
        self.channels = channels.split("-")
        self.premium = premium
        self.webhook = webhook
        self.username = username
        self.avatar = avatar
        self.toxicity = toxicity
        self.severe_toxicity = severe_toxicity
        self.obscene = obscene
        self.identity_attack = identity_attack
        self.insult = insult
        self.threat = threat
        self.sexual_explicit = sexual_explicit
        self.average = (
            self.toxicity
            + self.severe_toxicity
            + self.obscene
            + self.identity_attack
            + self.insult
            + self.threat
            + self.sexual_explicit
        ) / 7


class SentinelConfigModal(discord.ui.Modal, title="Sentinel Config"):
    """
    Config for sentinel
    """

    config = discord.ui.TextInput(
        label="Set config below, please only change the numbers",
        style=discord.TextStyle.long,
        placeholder="Type your feedback here...",
        required=True,
        max_length=500,
    )

    async def verify_input(self, config: str) -> bool:
        """
        Verify that the config is actually valid
        """

    async def pull_config(self, config: str) -> Config:
        """
        Pull a config from a config str"""

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"",
            description=f"""""",
            timestamp=discord.utils.utcnow(),
            color=style.Color.GREEN,
        )
        await interaction.response.send_message(embed=embed)


class SentinelWatcherView(discord.ui.View):
    """
    View for sentinel thingy
    """

    def __init__(self):
        """Init"""
        super().__init__()

    @discord.ui.button(label="Ban", emoji=":hammer:", style=discord.ButtonStyle.danger)
    async def ban(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.send("Add ban stuff idiot")

    @discord.ui.button(label="Mute", emoji=":mute:", style=discord.ButtonStyle.danger)
    async def mute(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.send("Add mute stuff here idiot")

    @discord.ui.button(
        label="warn", emoji=":warning:", style=discord.ButtonStyle.blurple
    )
    async def warn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.send("add warn stuff loser")


class SentinelConfigView(discord.ui.View):
    """
    The Sentinel Config View
    """

    def __init__(self):
        """Init"""
        super().__init__()

    @discord.ui.button(
        label="Update Config", emoji=":setting:", style=discord.ButtonStyle.grey
    )
    async def update_config(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.send_modal(SentinelConfigModal())


class Sentinel(commands.Cog):
    """
    Sentinel cog, drama watcher, moderation supreme, call it what you want
    """

    def __init__(self, bot):
        self.bot = bot
        self.sentinel = Detoxify(model_type="unbiased")
        self.sentinels = {}
        self.session = bot.sensession

    async def cog_load(self) -> None:
        """
        On cog load setup db
        """
        self.db = await asqlite.connect("Databases/sentinel.db")
        async with self.db.cursor() as cur:
            await cur.execute(
                """
                CREATE TABLE IF NOT EXISTS config (
                    guild           TEXT NOT NULL
                                        PRIMARY KEY,
                    channels        TEXT,
                    premium         BOOL NOT NULL,
                    webhook_url     TEXT NOT NULL,
                    username        TEXT,
                    avatar          TEXT,
                    webhook         INT NOT NULL,
                    toxicity        INT NOT NULL,
                    severe_toxicity INT NOT NULL
                    obscene         INT NOT NULL,
                    identity_attack INT NOT NULL,
                    insult          INT NOT NULL,
                    threat          INT NOT NULL,
                    sexual_explicit INT NOT NULL
                );
                """
            )
        await self.bot.printer.p_load("Sentinel Config")

    async def load_sentinels(self) -> None:
        """
        Load all sentinels objects into a cache so we can retrieve it quickly
        """
        async with self.db.cursor() as cursor:
            query = """SELECT * FROM config;"""
            data = await cursor.execute(query)
            for config in data:
                self.sentinels[config[0]] = Config(
                    config[1],
                    config[2],
                    config[3],
                    config[4],
                    config[5],
                    config[6],
                    config[7],
                    config[8],
                    config[9],
                    config[10],
                    config[11],
                    config[12],
                    config[13],
                )

    async def sentinel_check(self, msg: str) -> Toxicity:
        """
        Check for toxification
        """
        return Toxicity(self.sentinel.predict(msg))

    @commands.Cog.listener()
    async def on_message(self, msg):
        """
        Sentinels time :)
        """
        if msg.author.bot:
            return
        sentinel = self.sentinels.get(str(msg.guild.id))
        if not sentinel:
            pass
        elif msg.channel.id not in sentinel.channels:
            pass
        else:
            toxicness = await self.sentinel_check(msg.clean_content)
            if (
                toxicness.toxicity > sentinel.toxicity
                or toxicness.severe_toxicity > sentinel.severe_toxicity
                or toxicness.obscene > sentinel.obscene
                or toxicness.identity_attack > sentinel.identity_attack
                or toxicness.insult > sentinel.insult
                or toxicness.threat > sentinel.threat
                or toxicness.sexual_explicit > sentinel.sexual_explicit
                or toxicness.average > sentinel.average
            ):
                webhook = discord.Webhook.from_url(
                    sentinel.webhook_url,
                    adapter=discord.AsyncWebhookAdapter(self.session),
                )
                embed = discord.Embed(
                    title=f"Are you being toxic?",
                    description=f"""So rude.
                    toxicity: {toxicness.toxicity}%
                    severe_toxicity: {toxicness.severe_toxicity}
                    obscene: {toxicness.obscene}
                    identity_attack: {toxicness.identity_attack}
                    insult: {toxicness.insult}
                    threat: {toxicness.threat}
                    sexual_explicit: {toxicness.sexual_explicit}
                    average: {toxicness.average}""",
                    timestamp=discord.utils.utcnow(),
                    color=style.Color.RED,
                )
                await webhook.send(embed=embed)

        '''
        if msg.author.bot:
            pass
        elif msg.guild.id == 839605885700669441:
            toxic = await self.sentinel_check(msg.clean_content)
            if toxic.toxicity > 0.6:
                
                await msg.channel.send(embed=embed, delete_after=10)
        '''

    @commands.hybrid_group(
        name="sentinel",
        description="""View sentinel config""",
        help="""What the help command displays""",
        brief="Brief one liner about the command",
        aliases=[],
        enabled=True,
        hidden=False,
    )
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def sentinel_cmd(self, ctx):
        """
        Sentinel command, very cool
        """
        embed = discord.Embed(
            title=f"Sentinel Config",
            description=f"""
            """,
            timestamp=discord.utils.utcnow(),
            color=style.Color.RED,
        )
        embed.add_field(name="Current Config", value="Stuff")
        await ctx.send(embed=embed, view=SentinelConfigView())

    @sentinel_cmd.command(
        name="default",
        description="""Set default command config""",
        help="""Set sentinel config to default values.""",
        brief="You should also use this to setup",
        aliases=[],
        enabled=True,
        hidden=False
    )
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def sentinel_default_cmd(self, ctx):
        """Set default command config"""


async def setup(bot):
    await bot.add_cog(Sentinel(bot))
