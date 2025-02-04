# discord_utils.py
import os
import uuid
import asyncio
from functools import partial

from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from cassandra.policies import RoundRobinPolicy

import discord
from discord.ext import commands
from app.domain.services.news_service import NewsService
from app.schemas.news import NewsCreate
from app.domain.entities.user import User as UserModel
from app.domain.entities.news import News

from dotenv import load_dotenv

load_dotenv()

# Initialize the Cassandra connection
default_profile = ExecutionProfile(
    load_balancing_policy=RoundRobinPolicy(),
    request_timeout=30.0
)

cluster = Cluster(
    ['127.0.0.1'],
    port=9052,
    connect_timeout=10.0,
    execution_profiles={
        EXEC_PROFILE_DEFAULT: default_profile
    }
)
session = cluster.connect('lascaux')

# Register and set the default connection
connection.register_connection('default', session=session)
connection.set_default_connection('default')

# Synchronize the models
sync_table(News)
sync_table(UserModel)

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Configuration
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
DEFAULT_TAGS = ["General"]  # Default tag
DEFAULT_IMAGE_URL = os.getenv("DEFAULT_IMAGE_URL")
BOT_WALLET_ADDRESS = os.getenv("BOT_WALLET_ADDRESS")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    if message.channel.id == DISCORD_CHANNEL_ID:
        # Extract title and content from the message
        lines = message.content.strip().split("\n")
        if not lines:
            await message.channel.send("Message is empty. Please provide a title and content.")
            return

        title = lines[0]
        content = "\n".join(lines[1:]) if len(lines) > 1 else ""

        if not content:
            await message.channel.send("Please provide content for the news.")
            return

        # Extract image URL from attachments
        image_url = None
        if message.attachments:
            # Find the first attachment that is an image
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith("image/"):
                    image_url = attachment.url
                    break

        if not image_url:
            # Use the default image URL
            image_url = DEFAULT_IMAGE_URL

        # Create news data
        news_create = NewsCreate(
            title=title,
            content=content,
            tags=DEFAULT_TAGS,
            image_url=image_url
        )

        bot_uuid = uuid.uuid4()

        if not BOT_WALLET_ADDRESS:
            await message.channel.send("Bot wallet address is not configured.")
            return

        # Create an admin User instance for the bot.
        user = UserModel(
            id=bot_uuid,
            wallet_address=BOT_WALLET_ADDRESS,
            display_name=bot.user.name,
            roles=["admin"]
        )

        try:
            loop = asyncio.get_running_loop()
            create_news_func = partial(NewsService.create_news, news_create=news_create, user=user)
            await loop.run_in_executor(None, create_news_func)
            await message.channel.send(f"News titled '{title}' has been successfully saved to the platform.")
        except Exception as e:
            await message.channel.send(f"Failed to save news: {str(e)}")

    await bot.process_commands(message)
