import os
import aiohttp
import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SPACE_URL = os.getenv("SPACE_URL")

class SpiritClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Bot is ready and commands are synced.")

client = SpiritClient()

@client.tree.command(name="ask", description="Ask the Spirit Kings AI")
@app_commands.describe(prompt="Your message to the model")
async def ask(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                SPACE_URL,
                json={"prompt": prompt},
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(f"Error {resp.status}: {error_text}")
                data = await resp.json()
                reply = data.get("response") or "(no reply)"
        await interaction.followup.send(reply)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Failed to reach AI: {e}")

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user} (ID: {client.user.id})")

client.run(DISCORD_TOKEN)