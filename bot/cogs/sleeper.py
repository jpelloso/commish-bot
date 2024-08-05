import config
import sleeper_api
from discord.ext import commands
from openai import OpenAI

logger = config.get_logger(__name__)

class Sleeper(commands.Cog):

    error_message = "I'm having trouble getting that right now, please try again later"
    client = OpenAI(api_key=config.settings.openai_api_key)

    def __init__(self, bot):
        self.bot = bot
        self.sleeper_api = sleeper_api.Sleeper()
        self.generate_player_list()
        self.generate_draft_results()
        logger.debug("Sleeper cog initialized")

    def generate_player_list(self):
        # Please use this call sparingly, as it is intended only to be used once per day 
        # at most to keep your player IDs updated. The average size of this query is 5MB. 
        logger.info('generate player list')
        self.sleeper_api.get_player_list()

    def generate_draft_results(self):
        logger.info('generate draft results')
        self.sleeper_api.get_draft_results()

    @commands.command('regenerate_player_list')
    async def regenerate_player_list(self, ctx):
        logger.info('regenerate_player_list called')
        self.sleeper_api.get_player_list()

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user.mentioned_in(message):
            settings = str(self.sleeper_api.get_settings())
            draft = str(self.sleeper_api.get_draft_results())
            logger.info('replying to a bot mention')
            messages = [
                    {"role": "system", "content": "You only answer questions about the Sleeper league. Here are the league settings: {}".format(settings)},
                    {"role": "system", "content": "You only answer questions about the Sleeper keeper league. Players cannot keep players drafted in the first or seconds rounds. A player's keeper cost is one round higher than when they were drafted. If a player was not drafted, they would be a 7th or 8th round pick to keep. Here are the draft results: {}".format(draft)},
                    {"role": "user", "content": message.content}
               ]
            completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )

            await message.channel.send(completion.choices[0].message.content)
