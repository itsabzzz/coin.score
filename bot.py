import discord
from discord.ext import commands
from discord import app_commands
import config
from analyze import get_crypto_analysis

# Enable intents
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is online and ready to analyze crypto!")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

@bot.tree.command(name="analyze", description="Analyze a cryptocurrency.")
async def analyze(interaction: discord.Interaction, token: str):
    """Slash command to analyze a cryptocurrency"""
    await get_crypto_analysis(interaction, token)

bot.run(config.DISCORD_BOT_TOKEN)
