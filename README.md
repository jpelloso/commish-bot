# CommishBot
![Python](https://img.shields.io/badge/python-3.10-blue)

A Sleeper Fantasy sports bot for Discord

## Commands
    $ping                          - Return the latency of the bot
    $settings                      - Return the settings for the league
    $history                       - Return the league history
    $keeper [player]               - Return the round drafted of a specific player
    $poll [prompt]                 - Create a poll for the league to vote on

## Prerequisites
In order to properly configure your bot you will need the following:
* Discord API Token
* Discord Guild ID
* Sleeper League ID
* OpenAI API Key

### Discord API Token
1. Navigate to https://discord.com/developers/applications and click the ***New Application*** button
2. Give your application (bot) a name
3. Navigate to the **Bot** section under **Settings** and click the **Add Bot** button
4. Click the **Copy** button under **Token** to copy your bots API token to your clipboard

### OpenAI API Token
1. Navigate to https://platform.openai.com and create your account
2. Go to your project's **Dashboard** (create a default project if you have not already)
3. Select **API Keys** from the left navigation menu and select **Create new secret key** 

## Install and Run
### Locally
1. Clone this repository

        git clone git@github.com:jpelloso/commish-bot.git
        cd commish-bot
        
2. Configure the bot
   * Update `settings.toml` with the Discord token, Discord guild ID, and Sleeper league ID
   * Run `make configure` from the root directory to install python requirements

3. Run the bot

        make run

## Add Bot to Server
Follow the [instructions](https://discordpy.readthedocs.io/en/stable/discord.html#inviting-your-bot) below from discord.py to invite the bot to your server:
1. Make sure you’re logged on to the Discord website.
2. Navigate to the application page
3. Click on your bot’s page
4. Go to the “OAuth2” tab
5. Tick the “bot” checkbox under “scopes”
6. Tick the permissions required for your bot to function under “Bot Permissions”
7. Now the resulting URL can be used to add your bot to a server. Copy and paste the URL into your browser, choose a server to invite the bot to, and click “Authorize”

## Development
### Virtual Environments
```
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```
* `workon [venv]` - to activate or switch between virtual environments
* `deactivate` - to deactive the current virtual environment