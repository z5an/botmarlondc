import discord
from discord.ext import commands
from discord import app_commands
import random
import json
import os

# Konfiguration laden oder Standardwerte setzen
CONFIG_FILE = "config.json"
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
else:
    config = {
        "welcome_channel_id": None,
        "welcome_embed": {
            "title": "Willkommen!",
            "description": "Schön, dass du da bist, {member}!",
            "color": 0x00ff00
        },
        "auto_role_id": None,
        "auto_role_enabled": False,
        "verified_users": {}
    }

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Hilfsfunktion zum Speichern der Konfiguration
def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

# Willkommen-Event
@bot.event
async def on_member_join(member):
    if config["welcome_channel_id"]:
        channel = member.guild.get_channel(config["welcome_channel_id"])
        if channel:
            embed_cfg = config["welcome_embed"]
            embed = discord.Embed(
                title=embed_cfg.get("title", "Willkommen!"),
                description=embed_cfg.get("description", "").replace("{member}", member.mention),
                color=embed_cfg.get("color", 0x00ff00)
            )
            await channel.send(embed=embed)
    if config.get("auto_role_enabled") and config.get("auto_role_id"):
        role = member.guild.get_role(config["auto_role_id"])
        if role:
            await member.add_roles(role)

# Slash Command: Willkommen-Embed einstellen
@bot.tree.command(name="setwelcome", description="Stelle die Willkommensnachricht ein")
@app_commands.describe(
    channel="Kanal für Willkommensnachricht",
    title="Titel des Embeds",
    description="Beschreibung des Embeds (nutze {member} für den User)",
    color="Farbe als Hex (z.B. 0x00ff00)"
)
async def setwelcome(interaction: discord.Interaction, channel: discord.TextChannel, title: str, description: str, color: str):
    config["welcome_channel_id"] = channel.id
    config["welcome_embed"] = {
        "title": title,
        "description": description,
        "color": int(color, 16)
    }
    save_config()
    await interaction.response.send_message("Willkommensnachricht aktualisiert!", ephemeral=True)

# Slash Command: Auto-Rolle einstellen
@bot.tree.command(name="setautorole", description="Automatische Rolle für neue Mitglieder einstellen")
@app_commands.describe(
    role="Rolle, die vergeben werden soll",
    enabled="Automatische Rollenzuweisung aktivieren?"
)
async def setautorole(interaction: discord.Interaction, role: discord.Role, enabled: bool):
    config["auto_role_id"] = role.id
    config["auto_role_enabled"] = enabled
    save_config()
    await interaction.response.send_message(f"Auto-Rolle {'aktiviert' if enabled else 'deaktiviert'}!", ephemeral=True)

# Minecraft-Verify System (vereinfachtes Beispiel)
@bot.tree.command(name="verify", description="Verifiziere deinen Minecraft Account")
@app_commands.describe(
    minecraft_name="Dein Minecraft Name"
)
async def verify(interaction: discord.Interaction, minecraft_name: str):
    user_id = str(interaction.user.id)
    config["verified_users"][user_id] = minecraft_name
    save_config()
    await interaction.response.send_message(f"Dein Minecraft Account **{minecraft_name}** wurde verknüpft!", ephemeral=True)

# Slash Command: /cruch
@bot.tree.command(name="cruch", description="Wie viel Prozent Crush hast du auf jemanden?")
@app_commands.describe(
    user="Der User, auf den du einen Crush hast"
)
async def cruch(interaction: discord.Interaction, user: discord.User):
    percent = random.randint(0, 100)
    await interaction.response.send_message(
        f"💘 {interaction.user.mention} hat einen **{percent}% Crush** auf {user.mention}!"
    )

# Bot starten
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot ist online als {bot.user}.")

# Starte den Bot (Token eintragen)
if __name__ == "__main__":
    bot.run(os.environ["DISCORD_BOT_TOKEN"])
