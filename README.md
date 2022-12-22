# CommishBot
![Python](https://img.shields.io/badge/python-3.10-blue)

A Yahoo Fantasy sports bot for Discord

## Commands
    $ping                          - Return the latency of the bot
    $standings                     - Return the standings of the current season
    $matchups                      - Return the matchups for the current gameweek
    $playoffs                      - Return details about the playoffs for the current season
    $trade_deadline                - Return the last possible day for trades to be processed
    $roster [team]                 - Return the roster of a specific team
    $faab [team]                   - Return the FAAB balance of a specific team
    $manager [team]                - Return the manager nickname of a specific team
    $waiver [team]                 - Return the waiver position of a specific team
    $player_details [player]       - Return the details of a specific player
    $keeper [player]               - Return the round drafted of a specific player
    $history [year]                - Return the standings from a specific season
    $poll [prompt]                 - Create a poll for the league to vote on

## Prerequisites

In order to properly configure your bot you will need the following:

* Discord API Token
* Yahoo API Client ID & Secret
* Yahoo League ID

### Discord API Token

1. Navigate to https://discord.com/developers/applications and click the ***New Application*** button
2. Give your application (bot) a name
3. Navigate to the **Bot** section under **Settings** and click the **Add Bot** button
4. Click the **Copy** button under **Token** to copy your bots API token to your clipboard

### Yahoo API Client ID & Secret

1. Navigate to https://developer.yahoo.com/apps/ and click the **Create an App** button
2. Fill out the provided form, you can enter your own values for Application Name,  Description, and Homepage URL. Once complete click the **Create App** button
3. Copy the **Client ID** and **Client Secret** values

### Yahoo League ID

1. Navigate to your Yahoo! Fantasy League page
2. Under **League > Settings** you will find the **League ID**
3. Copy the **League ID**

## Install and Run

### Locally

1. Clone this repository

        git clone git@github.com:jpelloso/commish-bot.git
        cd commish-bot

2. Configure the bot

   * Create `.secrets.toml`
   
      ```
      cd config
      cp example.secrets.toml .secrets.toml
      ```
      
   * Update `.secrets.toml` with your secret keys, tokens, and league information
   
      ```
      [default]
      DISCORD_TOKEN = "discord-token"

      YAHOO_LEAGUE_ID = "123456"
      YAHOO_LEAGUE_TYPE = "nfl"
      YAHOO_KEY = "yahoo-key"
      YAHOO_SECRET = "yahoo-secret"
      ```
      
   * Run `make configure` from the root directory to install python requirements and get OAuth tokens
   
      ```
      cd ..
      make configure
      ```

3. Run the bot

        make run

### Heroku
Heroku apps include a [Procfile](Procfile) that specifies the commands that are executed by the app on startup and a [runtime.txt](runtime.txt) file that specifies the python version to use at runtime. The [Procfile](Procfile) should automatically create a Dyno on the **Resources** tab of the Heroku dashboard.
1. Connect you app to GitHub by navigating to the **Deploy** tab and authenticating Heroku with GitHub
2. Navigate to the **Settings** section and open up **Config Vars**. Create a environment variable for each entry in the `.secrets.toml` file in addition to `HEROKU_DEPLOYMENT=True`. Setting this value will ignore the `.secrets.toml` file which should not be pushed to GitHub
3. Navigate back to the **Deploy** section, choose a branch to deploy from and select **Deploy Branch**
4. Monitor the startup of the app with `heroku logs --tail -a discord-commish-bot` (requires Heroku CLI)
    * If you are unable to login via browser from Heroku CLI you can use `heroku login -i` to login directly from the terminal

## Add Bot to Server
Follow the [instructions](https://discordpy.readthedocs.io/en/stable/discord.html#inviting-your-bot) below from discord.py to invite the bot to your server:
1. Make sure you’re logged on to the Discord website.
2. Navigate to the application page
3. Click on your bot’s page
4. Go to the “OAuth2” tab
5. Tick the “bot” checkbox under “scopes”
6. Tick the permissions required for your bot to function under “Bot Permissions”
7. Now the resulting URL can be used to add your bot to a server. Copy and paste the URL into your browser, choose a server to invite the bot to, and click “Authorize”

