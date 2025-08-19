import config
import sleeper_api
import discord
from discord.ext import commands
from openai import OpenAI

logger = config.get_logger(__name__)

class Sleeper(commands.Cog):

    error_message = "I'm having trouble getting that right now, please try again later"
    client = OpenAI(api_key=config.settings.openai_api_key)

    def __init__(self, bot):
        self.bot = bot
        self.sleeper_api = sleeper_api.Sleeper()
        self.generate_draft_results()

        # Load bot context configuration from config
        self.prompt = config.settings.prompt.commishbot
        self.channels = config.settings.channels or {}
        self.personalities = config.settings.personalities or {}

        logger.debug("Sleeper cog initialized")

    def generate_draft_results(self):
        logger.info('generate draft results')
        self.sleeper_api.get_draft_results()

    async def get_channel_content(self, guild, channel_name, limit=20):
        channel = discord.utils.get(guild.channels, name=channel_name)
        if not channel:
            return ""

        all_text = []
        async for msg in channel.history(limit=limit):
            if msg.content:
                all_text.append(msg.content)
            for embed in msg.embeds:
                if embed.title:
                    all_text.append(embed.title)
                if embed.description:
                    all_text.append(embed.description)
                for field in embed.fields:
                    all_text.append(f"{field.name}: {field.value}")
                if embed.footer and embed.footer.text:
                    all_text.append(embed.footer.text)
        return "\n".join(all_text)

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user.mentioned_in(message) and not message.author.bot:
            sleeper_settings = str(self.sleeper_api.get_settings())
            draft_results = str(self.sleeper_api.get_draft_results())
            guild = message.guild
            logger.info('replying to a bot mention')

            # Build system messages for the model
            system_messages = [
                {
                    "role": "system",
                    "content": self.prompt
                }
            ]

            # Lookup author personality
            if self.personalities:
                personality = self.personalities.get(str(message.author.id))
                if personality:
                    system_messages.append({
                        "role": "system",
                        "name": "user-personality",
                        "content": f"Name: {personality['name']}\nPersonality: {personality['personality']}"
                    })

            # Add each channel's instructions + content as a separate system message
            if self.channels:
                for name, limit in self.channels.items():
                    channel_content = await self.get_channel_content(guild, name, limit)
                    system_messages.append({
                        "role": "system",
                        "name": name,
                        "content": channel_content
                    })

            system_messages.append({
                "role": "system",
                "name": "sleeper-settings",
                "content": sleeper_settings
            })

            system_messages.append({
                "role": "system",
                "name": "draft-results",
                "content": draft_results
            })

            system_messages.append({
                "role": "user",
                "content": message.content
            })

            # Call OpenAI
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=system_messages
            )

            await message.channel.send(completion.choices[0].message.content)
