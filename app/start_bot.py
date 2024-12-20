import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv

from app.utils.discord_utils import bot

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))  

# Run the bot
if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN or not DISCORD_CHANNEL_ID:
        print("Please set the DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID environment variables.")
    else:
        bot.run(DISCORD_BOT_TOKEN)