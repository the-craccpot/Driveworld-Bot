import discord
import openai
import os
from discord.ext import commands

# Load environment variables
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# Bot setup
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.channel.name in ["record entry", "user access"]:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.content}]
        )
        answer = response["choices"][0]["message"]["content"]
        await message.channel.send(answer)
    
    await bot.process_commands(message)

bot.run(TOKEN)
