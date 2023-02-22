
# NeiruBot 

## An AQW Guild utility Discord Bot

Make sure you have `python` installed in your system. [Click here to download](https://www.python.org/downloads/)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/R0mThz?referralCode=Qa9Rys)

**Follow the instructions to deploy and get it running:**


- Open your command prompt and move to a path, e.g `cd desktop`
- `git clone https://github.com/gneiru/NeiruBot.git`
- `cd NeiruBot`
- `pip install virtual env`
- `python -m venv env`
- Activate Environment depending on your OS
    - `env\scripts\activate` - For windows 
    - `source virtualenv_name/bin/activate` - For linux
- `pip install -r requirements.txt`
- Modifications before running the Bot
    - Rename **.env.example** into **.env** then change the following variables:
        - **TOKEN** - discord bot token from [Discord Developer Portal](https://discord.com/developers/applications), select an app > Bot > Copy Token
        - **LOGS_CHANNEL** - A channel ID for logging commands, you can ignore this unless you uncomment all commented lines in `cogs/on_error.py`
        - **MONGO_URI** - Database [connection string](https://www.mongodb.com/docs/guides/atlas/connection-string/) from mongodb to store Datas
        - **PREFIX** - Set a prefix, non-slash prefix, make sure no one use this as this is not recommended to use, not fully tested
        - Remaining variables are Twitter Developer Credentials, [click here for guide](https://www.joomshaper.com/documentation/joomla-extensions/sp-tweet/1-goto-https-dev-twitter-com-and-sign-in-with-your-twitter-account).

    - Change variables such as channel IDs in `modules/variables.py` 

- `python main.py`