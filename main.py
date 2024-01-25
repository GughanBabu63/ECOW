#from logging import RootLogger
from discord import interactions
from discord.flags import Intents
import discord
from discord.ext import commands
from cogs.challonge import Challonge
#from cogs.tours import Tours
from cogs.ticket import Ticket
#from cogs.registeration import Team_info_cog
from discord import app_commands
from keep_alive import keep_alive
import typing
import sqlite3
import os 

keep_alive()


def run():
  intents = discord.Intents.all()
  bot = commands.Bot(command_prefix="?", intents=intents)
  bot.remove_command("help")

  @bot.event
  async def on_ready():
    print("_______________________________")

    #print(await bot.load_extension('cogs.tours'))
    print(await bot.load_extension('cogs.challonge'))
    print(await bot.load_extension('cogs.ticket'))
    #print(await bot.load_extension('cogs.registeration'))
    activity = discord.Game(name="Hand-Crafted by R")
    await bot.change_presence(status=discord.Status.idle, activity=activity)
          
  bot.run(token="MTE4MTIyNjMxMDM3MTEyNzM5Nw.GF4V8B.IwvdTW9JRlb5OF0OwGNHWcW-GYbQHfliL7XI7o")


if __name__ == "__main__":
  run()
