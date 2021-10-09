#!/usr/bin/env python
import discord
from discord.ext import commands
import aiohttp
import asyncio
import json
import time
import traceback
import os
from watcher import Watcher
import random

refreshTime = 65		# WARNING - Setting below 15 seconds could violate Discord API ToS
loadTime = 5
client = None
clientReady = False
test_channel_id = 886703060078960674
prod_channel_id = 892254339928842260
TOKEN = os.environ.get("TOKEN")
url = ("https://api.mainnet-beta.solana.com")
watcher = Watcher("Hv3kURiwHKfGAq2a5jkHpC5mJsm95eKgi86WanEkZm3z", url)
random = ["We gunna mech it~", "Congratulations on meching it!","AYOOOOOOOO","GUNNA MECH IT", "LFGGGG"]
client = commands.Bot(command_prefix='.')

async def refreshThread():
  global refreshTime, client
  await client.wait_until_ready()
  channel = client.get_channel(id=test_channel_id)
  while not client.is_closed():
    async for i in watcher.fetchAccountHistory():
      res = json.loads(i[1])
      embedVar = discord.Embed(title=f"{res['name']} → SOLD", color=0xffffff)
      embedVar.set_thumbnail(url=f"{res['image']}")
      embedVar.add_field(name="Price (Sol)", value=i[0], inline=False)
      embedVar.add_field(name="Mint Token", value=i[2], inline=False)
      embedVar.set_footer(text="Sold on Magic Eden.")
      await channel.send(embed=embedVar)
    await asyncio.sleep(refreshTime)

def run(client):
  global TOKEN
  
  @client.event
  async def on_ready():
    global clientReady
    clientReady = True
    activity = discord.Activity(name='Mech Sales Bot', type=discord.ActivityType.watching)
    await client.change_presence(activity=activity)
    print(f'{client.user} has connected to Discord!')
  
  @client.event
  async def on_message(message):
    if message.author == client.user:
      return
    
    if message.content.startswith("Block"):
      await message.channel.send("Start")
    
    if message.content.startswith('.'):
      await client.process_commands(message)

  @client.command(pass_context=True)
  async def test(ctx):
    await ctx.send("testing")
  
  client.run(TOKEN)
  
def main():
  global client

  # Set up async fetch
  loop = asyncio.get_event_loop()
  loop.create_task(refreshThread())
  
  # Set up Discord
  run(client)
  
if __name__ == "__main__":
  main()