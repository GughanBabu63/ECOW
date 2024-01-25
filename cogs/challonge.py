import discord
from discord import role
from discord.ext import commands
from discord import app_commands
import base64
import gspread
import os
from discord.interactions import Interaction
import requests

import json
import asyncio
import sqlite3
from cogs.Challonges import api
from cogs.Challonges import tournament
#import button_paginator as pg
from cogs.cog_functions import challonge_req
from cogs.cog_functions import db_handler
import typing
import pandas as pd
from discord import utils
import gspread
from discord.utils import get


class Challonge(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.setups = []
    self.db = db_handler.SQL_Func()
    for guild in self.bot.guilds:
      for channel in guild.text_channels:
        if "ᴄʜᴀʟʟᴏɴɢᴇ" in channel.name.lower():
          self.setups.append([channel.id, channel.name, guild.name])
    self.cursor = challonge_req.Challonge_func()

    self.sheet_key = '1QoL3WMM-0PDLLNfD-PTaOiMmPZDeqGYVjB6SmOnPud0'
    sheet_credential = gspread.service_account('keys.json')
    self.spreadsheet = sheet_credential.open_by_key(self.sheet_key)
    worksheet = self.spreadsheet.worksheet('team_info')
    self.playing_teams = worksheet.col_values(1)
    print(self.playing_teams)

  async def auto_team_detail_autocompletion(
      self, ctx: commands.Context,
      current: str) -> typing.List[app_commands.Choice[str]]:
    data = [
        app_commands.Choice(name=team, value=team)
        for team in self.playing_teams
        if team.lower().startswith(current.lower())
    ]
    data = data[:24]
    return data

  @commands.hybrid_command(name="teams_info",
                           description="Load the tour player info")
  @app_commands.autocomplete(team_name=auto_team_detail_autocompletion)
  async def challonge_tournament(self, ctx, team_name: str):
    await ctx.defer()
    worksheet = self.spreadsheet.worksheet('team_info')
    k = worksheet.find(team_name)
    s = worksheet.row_values(int(k.row))
    col_name = worksheet.row_values(1)
    embed = discord.Embed(
        title=f"**{team_name}**",
        description=f"Here you can see all the info of the **{team_name}** team"
    )
    for i, j in enumerate(s):
      if j.isnumeric():
        j = discord.utils.get(ctx.guild.members, id=int(j))
        if j == None:
          embed.add_field(name=f"{col_name[i]}", value=f"**{j}**")
        else:
          embed.add_field(name=f"{col_name[i]}",
                          value=f"{j.name} - {j.mention}")
      else:
        embed.add_field(name=f"{col_name[i]}", value=f"**{j}**")
    file = discord.File('logo.png')
    embed.set_thumbnail(url="attachment://logo.png")
    embed.set_footer(text="Created & Managed by **ECOW**")
    await ctx.send(embed=embed)

  @commands.hybrid_command(name="auto_add_players",
                           description="Adding Players to the ticket")
  async def auto_add(self, ctx, category: discord.CategoryChannel):
    await ctx.defer()
    channels = category.channels
    channel_list = [[i.name, i.id] for i in channels]
    checking_name = []
    for j in channel_list:
      name = j[0].split("-")
      name = "".join(name)
      checking_name.append([name, j[1]])

    worksheet = self.spreadsheet.worksheet('team_info')
    team = []
    all_values = worksheet.get_all_records()
    for value in all_values:
      k = value['Team name'].lower()
      team.append([k.replace(" ", ""), value["Captain's Discord Id"]])
    for i in checking_name:
      print("Channel Name : ", i)
    print(len(team))
    final_list = []
    for i in checking_name:
      for l in team:
        if l[0] in i[0]:
          final_list.append([l[0], l[1], i[0], i[1]])
    prn_check = []
    for i in final_list:
      channel = discord.utils.get(ctx.guild.channels, id=int(i[3]))
      channel_name = channel.name
      channel_names = channel_name.split("-")
      team_name = channel.name[3::].split('-')
      team_name = "-".join(team_name)
      message = f"**MATCH INFO**\nMATCH : {channel.name}\nGROUP : {channel.name.split('-')[0]}\nROUND : {channel.name.split('-')[1]}\nTEAM_1 : {team_name.split('vs')[0].replace('-', ' ')}\nTEAM_2 : {team_name.split('vs')[1].replace('-', ' ')}\n\nDear Captains kindly discuss the schedule and ping the server helpers only when you both mutually decided the timing !."

      if message in prn_check:
        print("Hello")
      else:
        await channel.send(message)
        prn_check.append(message)

      member = discord.utils.get(ctx.guild.members, id=int(i[1]))
      await channel.send(
          f"\n``--------------------``\n{member.mention} is added to the room !."
      )
      await channel.set_permissions(member,
                                    view_channel=True,
                                    send_messages=True)
      await ctx.send("Players added to the battle room!")

  @commands.hybrid_command(name="ping", description="Bot Latency Check!")
  async def ping(self, ctx):
    await ctx.send('Pong! {0}'.format(round(self.bot.latency * 1000)))

  @commands.hybrid_command(name='refresh',
                           description="Refresh the team info data")
  async def refresh(self, ctx):
    await ctx.defer()
    self.sheet_key = '1QoL3WMM-0PDLLNfD-PTaOiMmPZDeqGYVjB6SmOnPud0'
    sheet_credential = gspread.service_account('keys.json')
    self.spreadsheet = sheet_credential.open_by_key(self.sheet_key)
    worksheet = self.spreadsheet.worksheet('team_info')
    self.playing_teams = worksheet.col_values(1)
    print(self.playing_teams)
    await ctx.send("Data Refreshed ! ")

  @commands.hybrid_command(
      name="get_tour",
      description="Provides information of any tour from challonge")
  async def challonge_tour(self, ctx, tour_id):
    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:
      await ctx.send("Role not set for the bot ")
    role_list = [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [
        int(role.id) for role in ctx.author.roles
    ]:
      self.cursor = challonge_req.Challonge_func()
      k = self.cursor.get_tournament(tournament_id=tour_id)
      embed = discord.Embed(
          title="TOURNAMENT DETAILS",
          description=
          "The basic informations about the tournament can be found here.")
      embed.add_field(name="Tournament Name", value=k[0][1], inline=False)
      embed.add_field(name="Tournament Id", value=k[0][0], inline=False)
      embed.add_field(name="Tournament Bracket", value=k[0][3], inline=False)
      embed.add_field(name="Tournament Type", value=k[0][2], inline=False)
      embed.add_field(name="Total No of Participants",
                      value=k[0][4],
                      inline=False)
      file = discord.File('logo.png')
      embed.set_thumbnail(url="attachment://logo.png")
      await ctx.reply(embed=embed, file=file)
    else:
      await ctx.reply("You dont  have the permission to use this command")

  @commands.hybrid_command(
      name="server_tours",
      description="Provides list of tournaments from challonge")
  async def challonge_tour_list(self, ctx):
    await ctx.defer()
    self.cursor = challonge_req.Challonge_func()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisors = self.challonge_supervisor[0][0][0]
      self.challonge_supervisors = int(self.challonge_supervisors)
    except:
      await ctx.send("Role not set for the bot ")
    role_list = [role.id for role in ctx.author.roles]
    if self.challonge_supervisors in [
        int(role.id) for role in ctx.author.roles
    ]:
      s = self.cursor.get_all_tournament()
      self.teams = [s[i][1] for i in range(len(s))]
      print(self.teams)
      embed = discord.Embed(
          title="**TOUR LIST OF ECOW**",
          description=
          "Here you can see the list of tours and its bracket by ECOW")
      for i in range(len(s)):
        embed.add_field(name=f"**{s[i][1]}**",
                        value=f"{s[i][3]}",
                        inline=False)
      embed.set_footer(text='created and managed by ECOW')
      file = discord.File('logo.png')
      embed.set_thumbnail(url="attachment://logo.png")
      await ctx.reply(embed=embed, file=file)
      log_channel = self.db.fetch_log_channelid()
      print(log_channel)
      channel = self.bot.get_channel(int(log_channel[0][0]))
      embed = discord.Embed(title="TOURS LOADED !",
                            description="Tour list updated from challonge!")
      await channel.send(embed=embed)
    else:
      await ctx.send("You don't have the permission to use this command ! ")

  async def rounds_autocompletion(
      self, ctx: commands.Context,
      current: str) -> typing.List[app_commands.Choice[str]]:
    data = []
    for drink_choice in ["1", "2", "3", "4", "5", "6", "7", "8"]:
      if current.lower() in drink_choice.lower():
        data.append(app_commands.Choice(name=drink_choice, value=drink_choice))
    return data

  async def group_autocompletion(
      self, ctx: commands.Context,
      current: str) -> typing.List[app_commands.Choice[str]]:
    data = []
    for drink_choice in ["a", "b", "c", "d", "e"]:
      if current.lower() in drink_choice.lower():
        data.append(app_commands.Choice(name=drink_choice, value=drink_choice))
    return data

  async def teams_autocompletion(
      self, ctx: commands.Context,
      current: str) -> typing.List[app_commands.Choice[str]]:
    data = [
        app_commands.Choice(name=team, value=team) for team in self.teams
        if team.lower().startswith(current.lower())
    ]
    data = data[:24]
    return data

  @commands.hybrid_command(name="load_tournament",
                           description="Load the tournament to the database")
  @app_commands.autocomplete(tournament=teams_autocompletion)
  async def app_challonge_tournament(self, ctx, tournament: str):
    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:
      await ctx.send("Role not set for the bot ")
    role_list = [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [
        int(role.id) for role in ctx.author.roles
    ]:
      self.cursor = challonge_req.Challonge_func()
      self.db = db_handler.SQL_Func()
      s = self.cursor.get_all_tournament()
      k = []
      for i in s:
        if tournament == i[1]:
          k.append(i)

      self.db.insert_tournament(s)
      tournnament_name = self.db.fetch_one_tournament(tournament)
      embed = discord.Embed(
          title="TOURNAMENT LOADED INFO",
          description=
          f"The **{tournnament_name[0][1]}** tournament has been loaded to the database !"
      )
      file = discord.File('logo.png')
      embed.set_thumbnail(url="attachment://logo.png")
      self.teams = [tournnament_name[0][1]]
      await ctx.reply(embed=embed)
      log_channel = self.db.fetch_log_channelid()
      print(log_channel)
      channel = self.bot.get_channel(int(log_channel[0][0]))
      await channel.send(embed=embed)
    else:
      await ctx.send("You don't have the permission to use this bot")

  @commands.hybrid_command(name="load_players",description="Loads players of the selected tournament to DB")
  @app_commands.autocomplete(item=teams_autocompletion)
  async def tournament_players(self, ctx: commands.Context, item: str):
    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:
      await ctx.send("Role not set for the bot ")
    role_list = [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [
        int(role.id) for role in ctx.author.roles
    ]:
      tournament = self.db.fetch_one_tournament(item)
      players = self.cursor.get_all_participants(tournament_id=tournament[0])
      self.db.insert_tournament_players(players)
      self.tour_players = self.db.fetch_all_players(tournament[0][0])
      print(self.tour_players)
      await ctx.send("Tour Participants are Loaded to DB!")
    else:
      await ctx.send("You don't have the permission to use this command !")

  @commands.hybrid_command(name="clear_tours",
                           description="Clears all tournaments from DB")
  async def clear_tours(self, ctx: commands.Context):
    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:
      await ctx.send("Role not set for the bot ")
    role_list = [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [
        int(role.id) for role in ctx.author.roles
    ]:
      self.db.create_tournament_table()
      self.db.drop_tournament()
      embed = discord.Embed(
          title="**ECOW TOURS TABLE DELETED !**",
          description=f"The tour table was deleted by {ctx.author.mention}")
      await ctx.reply(embed=embed)
      log_channel = self.db.fetch_log_channelid()
      print(log_channel)
      channel = self.bot.get_channel(int(log_channel[0][0]))
      await channel.send(embed=embed)
    else:
      await ctx.send("You don't have the permission to use this command ! ")

  @commands.hybrid_command(name="clear_matches",
                           description="Clears all tournaments from DB")
  async def clear_matches(self, ctx: commands.Context):
    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:
      await ctx.send("Role not set for the bot ")
    role_list = [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [
        int(role.id) for role in ctx.author.roles
    ]:
      self.db.drop_tournament_matches()
      self.db.create_tournament_matches()
      embed = discord.Embed(
          title="**ECOW MATCHES TABLE DELETED !**",
          description=f"The match table was deleted by {ctx.author.mention}")
      await ctx.reply(embed=embed)
      log_channel = self.db.fetch_log_channelid()
      print(log_channel)
      channel = self.bot.get_channel(int(log_channel[0][0]))
      await channel.send(embed=embed)
    else:
      await ctx.send("You don't have the permission to use this command")

  @commands.hybrid_command(name="clear_players",
                           description="Clears all players data from DB")
  async def clear_players(self, ctx: commands.Context):
    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:
      await ctx.send("Role not set for the bot ")
    role_list = [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [
        int(role.id) for role in ctx.author.roles
    ]:
      self.db.drop_tournament_players()
      self.db.create_tournament_players()
      embed = discord.Embed(
          title="**ECOW PLAYERS TABLE DELETED !**",
          description=f"The players table was deleted by {ctx.author.mention}")
      await ctx.reply(embed=embed)
      log_channel = self.db.fetch_log_channelid()
      print(log_channel)
      channel = self.bot.get_channel(int(log_channel[0][0]))
      await channel.send(embed=embed)
    else:
      await ctx.send("You don't have the permission to use this command!")

  @commands.hybrid_command(
      name="ongoing_matches",
      description="Shows the ongoing matches from the tour")
  @app_commands.autocomplete(item=teams_autocompletion)
  async def ongoing_matches(
      self,
      ctx: commands.Context,
      item: str,
  ):
    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:
      await ctx.send("Role not set for the bot ")
    role_list = [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [
        int(role.id) for role in ctx.author.roles
    ]:
      await ctx.send(
          "Hello Supervisor , Kindly wait let me grab the new matches found in challonge!"
      )
      #self.db.drop_tournament_matches()
      #await ctx.send("Old Data Cleared !")
      self.cursor = challonge_req.Challonge_func()
      self.db = db_handler.SQL_Func()
      tournament = self.db.fetch_one_tournament(item)
      matches = self.cursor.get_all_matches(tournament_id=tournament[0])
      #self.players = self.cursor.get_all_participants(
      #    tournament_id=tournament[0])
      lk = self.db.fetch_all_players(tournament[0][0])
      final_list = []
      for i in matches:
        tournament_name = item
        tournament_id = i[0]
        match_id = i[1]
        player_1 = self.db.fetch_one_player(i[2])
        if len(player_1) == 0:
          player_1 = None
        else:
          player_1 = player_1[0][3]
        player_2 = self.db.fetch_one_player(i[3])
        if len(player_2) == 0:
          player_2 = None
        else:
          player_2 = player_2[0][3]
        match_name = f"{player_1} vs {player_2}"
        score = i[4]
        winner = self.db.fetch_one_player(i[5])
        if len(winner) == 0:
          winner = None
        else:
          winner = winner[0][2]
        state = i[6]
        final_list.append((match_name, tournament_name, tournament_id,
                           match_id, player_1, player_2, score, winner, state))
      print(final_list)
      self.db.insert_tournament_matches(final_list)
      k = self.db.fetch_all_matches()
      self.k = [i[0] for i in k]
      await ctx.send("Tournament Matches Tables Updated !")
    else:
      await ctx.send("You don't have the permission to use this command !")

  async def matches_autocompletion(
      self, ctx: commands.Context,
      current: str) -> typing.List[app_commands.Choice[str]]:
    data = []
    for drink_choice in [i for i in self.k if "None" not in i]:
      if current.lower() in drink_choice.lower():
        data.append(app_commands.Choice(name=drink_choice, value=drink_choice))
    return data

  @commands.hybrid_command(name="upload_score",
                           description="Uploads score of a match")
  @app_commands.autocomplete(item=matches_autocompletion)
  async def Score_matches(self,
                          ctx: commands.Context,
                          item: str,
                          team1_score=0,
                          team2_score=0):
    await ctx.defer()
    tournament_id = self.db.fetch_one_tournament_id(item)
    tournament_id = tournament_id[0][2]
    players = item.split(" vs ")
    player_1 = players[0]
    player_2 = players[1]
    player_1_id = self.db.fetch_one_player_name(player_1)[0][0]
    player_1_main_id = self.db.fetch_one_player_name(player_1)[0][1]
    player_2_id = self.db.fetch_one_player_name(player_2)[0][0]
    player_2_main_id = self.db.fetch_one_player_name(player_2)[0][1]
    match_id = self.db.fetch_one_match_id(item)
    winner_name = ""
    winner = max(int(team1_score), int(team2_score))
    if winner == int(team1_score):
      winner = player_1_id
      winner_main_id = player_1_main_id
      winner_name = player_1
    else:
      winner = player_2_id
      winner_name = player_2
      winner_main_id = player_2_main_id
    score = f"{team1_score}-{team2_score}"
    value = [tournament_id, match_id[0], winner, score]
    values = [tournament_id, match_id[0], winner_main_id, score]
    result_channel = self.db.fetch_result_channelid()
    ch = result_channel[0][0]
    category_name = ctx.channel.category.name
    result_channel = discord.utils.get(ctx.guild.channels, id=int(ch))
    print("result channel :", result_channel.name, result_channel.id)
    embed = discord.Embed(
        title=f"**{category_name}**",
        description=
        f"This is the updated report of the **{item}** from challonge!")
    embed.add_field(name="match", value=f"✅{item}")
    embed.add_field(name="score", value=f"**{score}**", inline=False)
    embed.add_field(name="winner",
                    value=f"**🎖️{winner_name}**- won the match",
                    inline=True)
    embed.add_field(name="Battle-Ticket",
                    value=ctx.channel.mention,
                    inline=False)
    embed.set_footer(text="Created and Managed by **ECOW**")
    k = self.cursor.update_score([value, values])
    message = await result_channel.send(embed=embed)
    message_link = f'https://discord.com/channels/{ctx.guild.id}/{int(result_channel.id)}/{message.id}'
    mesem = discord.Embed(title="",
                          description=f"🎖️**Result Uploaded**",
                          color=discord.Color.red())
    mesem.add_field(name=f"{ctx.author.mention} uploaded the result !",
                    value="")
    mesem.add_field(name=f"**link -> {message_link}**", value=f"", inline=True)
    await ctx.send(embed=mesem)

  @commands.hybrid_command(name="clear_config",
                           description="clear_configuration of challonge")
  async def clear_config(self, ctx: commands.Context):
    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:
      await ctx.send("Role not set for the bot ")
    role_list = [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [
        int(role.id) for role in ctx.author.roles
    ]:
      self.db.clear_config()
      log_channel = self.db.fetch_log_channelid()
      print(log_channel)
      channel = self.bot.get_channel(int(log_channel[0][0]))
      embed = discord.Embed(
          title="**️ Challonge Configuration Cleared**",
          description=
          f"{ctx.author.mention} has cleared the challonge configuration",
          color=discord.Color.green())
      await channel.send(embed=embed)
    else:
      await ctx.send("You don't have the permission to use this command ! ")

  @clear_matches.error
  @clear_tours.error
  @clear_players.error
  @Score_matches.error
  @ongoing_matches.error
  async def role_missing_error(self, ctx: commands.Context, error):
    if isinstance(error, commands.MissingRole):
      message = f" ```{ctx.author.mention} tried to use a restricted command , Message link : {ctx.message.jump_url}``` "
      log_channel = self.db.fetch_log_channelid()
      print(log_channel)
      channel = self.bot.get_channel(int(log_channel[0][0]))
      await channel.send(message)
      m = await ctx.reply("you don't have permissions !")

  async def challonge_panel_autocompletion(
      self, ctx: commands.Context,
      current: str) -> typing.List[app_commands.Choice[str]]:
    data = []
    for drink_choice in [i[1] for i in self.setups]:
      if current.lower() in drink_choice.lower():
        data.append(app_commands.Choice(name=drink_choice, value=drink_choice))
    return data





 
      
      
   

  @commands.hybrid_command(name="challonge_role_setup",description="Setup challonge bot role")
  async def challonge_role_id(self, ctx,role: discord.Role,result_channel:str,testing_channel:str,log_channel:str):
    await ctx.defer()
    role = role_id.id
    s = self.db.insert_challonge_role(role)
    self.challonge_supervisor = self.db.fetch_challonge_role_id()[0][0]
    s = self.db.insert_result(i)
    embed = discord.Embed(title="**CHALLONGE SETUP PANNEL**",description= "Challonge Bot Settings")
    embed.add_field(name=f" ROLE : <@&{self.challonge_supervisor}>",value="")
    
    result_channel = discord.utils.get(ctx.guild.channels,id=result_channel)
    self.db.insert_result(result_channel.id)
    embed.add_field(name=f"RESULT -> {result_channel.mention}",value="")
    
    testing_channel = discord.utils.get(ctx.guild.channels,id=testing_channel)
    self.db.insert_testing(testing_channel.id)
    embed.add_field(name=f"TESTING -> {testing_channel.mention}",value="")
    
    log_channel = discord.utils.get(ctx.guild.channels,id=log_channel)
    self.db.insert_log(log_channel.id)
    embed.add_field(name=f"LOG -> {log_channel.mention}",value="")
    await ctx.reply(embed=embed)

  async def team_detail_autocompletion(
      self, ctx: commands.Context,
      current: str) -> typing.List[app_commands.Choice[str]]:
    data = [
        app_commands.Choice(name=team, value=team)
        for team in self.playing_teams
        if team.lower().startswith(current.lower())
    ]
    data = data[:24]
    return data

  
  @commands.hybrid_command(name="open_room",description="Opens battle tickets for selected round of a tour.")
  @app_commands.autocomplete(item=teams_autocompletion)
  async def open_room(self, ctx, round, item: str):

    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:
      await ctx.send("Role not set for the bot ")
    role_list = [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [
        int(role.id) for role in ctx.author.roles
    ]:
      tournaments = self.db.fetch_one_tournament(item)
      tournament_id = tournaments[0][0]
      await ctx.send(f"Fetching Matches From Challonge...")
      #await ctx.send(f"Room {round} is opening under the {categories.name}!")
      api.launch("Rayleigh63", "yap4bTPYqHDaiKI3ZOb1m6qXJrvfRaZYwbPIvqgu")
      tour = tournament.show(int(tournament_id), 1, 1)
      t_cursor = tour['tournament']
      m_cursor = tour['tournament']['matches']
      p_cursor = tour['tournament']['participants']
      tournament_info = [
          t_cursor['name'], t_cursor['id'],
          "https://challonge.com/" + t_cursor['url'],
          t_cursor['participants_count']
      ]
      #print(tournament_info)
      match_info = [[
          i['match']['id'], i['match']['tournament_id'], tournament_info[0],
          i['match']['player1_id'], i['match']['player2_id'],
          i['match']['state'], i['match']['winner_id'],
          i['match']['scores_csv'], i['match']['round'], i['match']['group_id']
      ] for i in m_cursor]
      #print(match_info[0:4])
      try:
        participants_info = [[
            i['participant']['id'], i['participant']['tournament_id'],
            i['participant']['name'], i['participant']['group_player_ids'][0]
        ] for i in p_cursor]
      except:
        participants_info = [[
            i['participant']['id'], i['participant']['tournament_id'],
            i['participant']['name'], i['participant']['id']
        ] for i in p_cursor]
      #print(participants_info[0:4])
      groups = ['a', 'b', 'c', 'd','e','f','g','h','i','j']
      group_ids = []
      for i in m_cursor:
        k = i['match']['group_id']
        if k not in group_ids:
          group_ids.append(k)
      print(group_ids)
      group_ids = [[groups[i], j] for i, j in enumerate(group_ids)]
      match_list = []
      for i in match_info:
        if i[5] == "pending" or i[5] == "open":
          player1_name = [
              j[2] for j in participants_info if j[0] == i[3] or j[3] == i[3]
          ]
          player2_name = [
              j[2] for j in participants_info if j[0] == i[4] or j[3] == i[4]
          ]
          if len(player1_name) > 0 and len(player2_name) > 0:
            for group in group_ids:
              if group[1] == i[-1]:
                match_name = f"{player1_name[0]} vs {player2_name[0]}"
                match_list.append([
                    str(group[0]) + " " + "r" + str(i[-2]) + " " + match_name,
                    i
                ])
      db = db_handler.SQL_Func()
      s = db.fetch_ticket_setup(ctx.guild.id)
      s = [j for j in s]
      print(s)
      open_category = int(s[0][1])
      transcript_channel = int(s[0][4])
      log_channel = int(s[0][3])
      print(open_category, "open")
      log_channel = discord.utils.get(ctx.guild.channels, id=log_channel)
      categories = discord.utils.get(ctx.guild.categories, id=open_category)
      print(match_list)
      for i in match_list:
        mr = str(i[0]).split(" ")[1]
        if len(mr) > 1 and mr[1] == round:
          print("i", i)
          ticket_checker = discord.utils.get(categories.text_channels,
                                             name=f"{i[0]}")
          if ticket_checker is not None:
            await ctx.send(f"{i[0]} is already opened !")
          else:
            roles = s[0][-1].split("-")
            roles = [int(i) for i in roles]
            overwrites = {
                ctx.guild.default_role:
                discord.PermissionOverwrite(view_channel=False),
                ctx.guild.me:
                discord.PermissionOverwrite(read_message_history=True,
                                            view_channel=True,
                                            send_messages=True,
                                            manage_messages=True,
                                            manage_channels=True,
                                            manage_roles=True)
            }
            for k in roles:
              overwrites = overwrites | {
                  ctx.guild.get_role(int(k)):
                  discord.PermissionOverwrite(read_message_history=True,
                                              view_channel=True,
                                              send_messages=True,
                                              manage_messages=True,
                                              manage_channels=True,
                                              manage_roles=True)
              }
            await categories.create_text_channel(f'{i[0]}',
                                                 overwrites=overwrites)
            trans_channel = discord.utils.get(ctx.guild.channels,
                                              id=transcript_channel)
      embed = discord.Embed(
          title=
          f"Room Opened for {round} by {ctx.author.mention} under {categories.mention} ",
          description="")
      await log_channel.send(embed=embed)
      await ctx.send(f"Room for round-{round} Opened Successfully!",
                     ephemeral=True)
    else:
      await ctx.send("You don't have the permission to use this command !")


async def setup(bot):
  await bot.add_cog(Challonge(bot))
