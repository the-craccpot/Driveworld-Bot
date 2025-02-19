import discord
import openai
import os
from discord.ext import commands

# Load environment variables
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PRICING_CHANNEL_ID = os.environ.get("PRICING_CHANNEL_ID")
RECORD_ENTRY_CHANNEL_ID = os.environ.get("RECORD_ENTRY_CHANNEL_ID")

print("Environment Variables:")
print(os.environ)  # Debugging line

print("Bot Token:", TOKEN)  # Debugging line

openai.api_key = OPENAI_API_KEY

# Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if str(message.channel.id) in [PRICING_CHANNEL_ID, RECORD_ENTRY_CHANNEL_ID]:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.content}]
        )
        answer = response["choices"][0]["message"]["content"]
        await message.channel.send(answer)
    
    await bot.process_commands(message)

bot.run(TOKEN)
