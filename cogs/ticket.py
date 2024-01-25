# Create a new file called cog_example.py
# Import the necessary modules
#from _typeshed import Self
import discord
from discord import message
from discord.ext import commands
from discord import app_commands
import traceback
from cogs import Challonges
from cogs.Challonges import api
from cogs.Challonges import tournament
from cogs.cog_functions import challonge_req
from cogs.cog_functions import db_handler
import chat_exporter
import io
import asyncio


# Create a class for your cog
class Ticket(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    print("Tickets cog loaded")

  @commands.hybrid_command(name="show_setup",
                           description="Shows the setup for the ticket system")
  async def show_setup(self, ctx):
    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:
      await ctx.send("Role not set for the bot ")
    role_list =   [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [int(role.id) for role in ctx.author.roles]:
      db = db_handler.SQL_Func()
      s = db.fetch_ticket_setup(ctx.guild.id)
      db = db_handler.SQL_Func()
      s = db.fetch_ticket_setup(ctx.guild.id)
      s = [j for j in s]
      print(s)
      log_channel = int(s[0][3])
      transcrip_channel = int(s[0][4])
      ticket_category = int(s[0][1])
      close_category = int(s[0][2])
      log_channel = discord.utils.get(ctx.guild.channels, id=log_channel)
      trans_channel = discord.utils.get(ctx.guild.channels, id=transcrip_channel)
      ticket_category = discord.utils.get(ctx.guild.categories,
                                          id=ticket_category)
      close_category = discord.utils.get(ctx.guild.categories, id=close_category)
      embed = discord.Embed(title="**Configuration Info**",
                            color=discord.Color.dark_gold())
      embed.add_field(name="**Action** : **Setup**", value="", inline=True)
      embed.add_field(name='**------------------------**', value="", inline=True)
      embed.add_field(name=f"User  : {ctx.author.mention}",
                      value="",
                      inline=True)
      embed.add_field(name=f"Open :",
                      value=f"{ticket_category.mention}",
                      inline=False)
      embed.add_field(name=f"Close :",
                      value=f"{close_category.mention}",
                      inline=False)
      embed.add_field(name=f"Transcript :",
                      value=f"{trans_channel.mention}",
                      inline=False)
      embed.add_field(name=f"Logs :",
                      value=f"{log_channel.mention}",
                      inline=False)
      embed.add_field(
          name=f"Roles :",
          value=
          f"{[ctx.guild.get_role(int(k)).mention for k in s[0][-1].split('-') ]}",
          inline=False)
      embed.set_footer(text="Created & Managed by ECOW")
      await ctx.send(embed=embed)
    else:
      await ctx.send("You don't have the permission to use this command !")
  
  @commands.hybrid_command(name="pannel_setup", description="Setup tour pannel")
  async def setup(self, ctx, ticket_category: discord.CategoryChannel,
                  close_category: discord.CategoryChannel, log_channel,
                  transcript_channel):
    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:      await ctx.send("Role not set for the bot ")
    role_list =   [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [int(role.id) for role in ctx.author.roles]:
      server_roles = ctx.guild.roles
      server_categories = ctx.guild.categories
      print(server_roles)
      print(server_categories)
  
      role_select = discord.ui.Select(options=[
          discord.SelectOption(label=i.name, value=i.id) for i in ctx.guild.roles
          if i.permissions.manage_channels
      ][:20],
                                      placeholder="Select a role",
                                      min_values=1,
                                      max_values=10)
  
      async def select_callback(interaction: discord.Interaction):
        await interaction.response.defer()
        db = db_handler.SQL_Func()
        db.insert_ticket_setup([
            ctx.guild.id, ticket_category.id, close_category.id, log_channel,
            transcript_channel, "-".join(role_select.values)
        ])
        s = db.fetch_ticket_setup(ctx.guild.id)
        for i in s:
          print(s)
        db = db_handler.SQL_Func()
        s = db.fetch_ticket_setup(ctx.guild.id)
        s = [j for j in s]
        transcrip_channel = int(s[0][4])
        logs_channel = int(s[0][3])
        logs_channel = discord.utils.get(ctx.guild.channels, id=logs_channel)
        trans_channel = discord.utils.get(ctx.guild.channels,
                                          id=transcrip_channel)
        embed = discord.Embed(title="**Configuration Info**",
                              color=discord.Color.dark_gold())
        embed.add_field(name="**Action** : **Setup**", value="", inline=True)
        embed.add_field(name='**------------------------**',
                        value="",
                        inline=True)
        embed.add_field(name=f"User  : {ctx.author.mention}",
                        value="",
                        inline=True)
        embed.add_field(name=f"Open :",
                        value=f"{ticket_category.mention}",
                        inline=False)
        embed.add_field(name=f"Close :",
                        value=f"{close_category.mention}",
                        inline=False)
        embed.add_field(name=f"Transcript :",
                        value=f"{trans_channel.mention}",
                        inline=False)
        embed.add_field(name=f"Log :",
                        value=f"{logs_channel.mention}",
                        inline=False)
        embed.add_field(
            name=f"Roles :",
            value=
            f"{[interaction.guild.get_role(int(k)).mention for k in role_select.values ]}",
            inline=False)
        embed.set_footer(text="Created & Managed by ECOW")
        message = await logs_channel.send(embed=embed)
        message_link = f'https://discord.com/channels/{ctx.guild.id}/{int(s[0][3])}/{message.id}'
        await asyncio.sleep(5)
        await interaction.response.send_message(
            f"🗒️ Setup Completed -> [{message_link}]")
  
      role_select.callback = select_callback
      print("role", role_select.values)
      view = discord.ui.View()
      view.add_item(role_select)
  
      await ctx.send("Select the drop down to make setup", view=view)
    else:
      await ctx.send("You don't have the permission to use the bot !")
      
  @commands.command()
  async def syncs(self, ctx):
    self.bot.tree.copy_global_to(guild=ctx.guild)
    await self.bot.tree.sync()
    await ctx.reply("```Commands synced to the server ! ```")

  # Add your commands
  @commands.hybrid_command(name="alive",description="check bot presence")
  async def alive(self, ctx):
    await ctx.send("I am still on the battlefield boss !")

  

  @commands.hybrid_command(name="clear_category",description="Clears all the tickets in the selected category")
  async def clear_category(self, ctx, category: discord.CategoryChannel):
    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:
      await ctx.send("Role not set for the bot ")
    role_list =   [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [int(role.id) for role in ctx.author.roles]:
      await ctx.send(f"Cleaning category {category.name}")
      channels = category.channels
      for channel in channels:
        await channel.send('The channel will be deleted in 2 seconds')
        await asyncio.sleep(2)
        db = db_handler.SQL_Func()
        s = db.fetch_ticket_setup(ctx.guild.id)
        s = [j for j in s]
        logger_channel = int(s[0][3])
        log_channel = discord.utils.get(ctx.guild.channels, id=logger_channel)
        embed = discord.Embed(title="**Logged Info**", color=discord.Color.red())
        embed.add_field(name=f"**Ticket :**",
                        value=f"{channel.name}",
                        inline=True)
        embed.add_field(name="**Action** : **Channel Deleted**",
                        value="",
                        inline=True)
        embed.add_field(name=f"User   : {ctx.author.mention}",
                        value="",
                        inline=True)
        embed.set_footer(text="Created & Managed by ECOW")
        await log_channel.send(embed=embed)
        await channel.delete()
    else:
       await ctx.send("You don't have the permission to use this command")

  @commands.hybrid_command(name="rename",description="rename the battle ticket")
  async def rename(self, ctx, name):
    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:
      await ctx.send("Role not set for the bot ")
    role_list =   [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [int(role.id) for role in ctx.author.roles]:
      try:
        channel = ctx.channel
        oldname = channel.name
        await channel.edit(name=f"{name}")
        await ctx.send("Channel renamed successfully",ephemeral=True)
        db = db_handler.SQL_Func()
        s = db.fetch_ticket_setup(ctx.guild.id)
        s = [j for j in s]
        logger_channel = int(s[0][3])
        log_channel = discord.utils.get(ctx.guild.channels, id=logger_channel)
        embed = discord.Embed(title="**Logged Info**",
                              color=discord.Color.blue())
        embed.add_field(name=f"**Ticket :**",
                        value=f"{ctx.channel.name}",
                        inline=True)
        embed.add_field(name="**Action** : **Channel Renamed**",
                        value="",
                        inline=True)
        embed.add_field(name=f"User   : {ctx.author.mention}",
                        value="",
                        inline=True)
        embed.set_footer(text="Created & Managed by ECOW")
        await log_channel.send(embed=embed)
      except:
        pass
    else:
      await ctx.send("You don't have permission to use this command !")
      
  
  @commands.hybrid_command(name="bulk_role_assign",description="Assign role to all members in bulk")
  async def bulk_role_assign(self, ctx, role: discord.Role):
    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:
      await ctx.send("Role not set for the bot ")
    role_list =   [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [int(role.id) for role in ctx.author.roles]:
      await ctx.send(
          "``Please ensure that column name should be  Id``"
      )
      message = await self.bot.wait_for('message')
      if str(message.attachments
             ) == "[]":  # Checks if there is an attachment on the message
        return
      else:  # If there is it gets the filename from message.attachments
        split_v1 = str(message.attachments).split("filename='")[1]
        filename = str(split_v1).split("' ")[0]
        if filename.endswith(".csv"):  # Checks if it is a .csv file
          await message.attachments[0].save(fp="CsvFiles/{}".format(filename))
      import pandas as pd
      df = pd.read_csv(f"CsvFiles/{filename}")
      k = df['Id'].to_list()
      for i in k:
        member = ctx.guild.get_member(int(i))
        await member.add_roles(role)
        await ctx.send(f'{role.mention} Role added to {member.mention}')
      await ctx.send(f'Role added to {len(k)} members')
    else:
      await ctx.send("You don't have the permission to use this command !")

  @commands.hybrid_command(name="add",description="Add member to the ticket")
  async def add(self, ctx, user: discord.Member):
    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:
      await ctx.send("Role not set for the bot ")
    role_list =   [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [int(role.id) for role in ctx.author.roles]:
      await ctx.channel.set_permissions(user,
                                        read_messages=True,
                                        send_messages=True,
                                        attach_files=True,
                                        read_message_history=True,
                                        view_channel=True,
                                        add_reactions=True,
                                        embed_links=True)
  
      db = db_handler.SQL_Func()
      s = db.fetch_ticket_setup(ctx.guild.id)
      s = [j for j in s]
      logger_channel = int(s[0][3])
      log_channel = discord.utils.get(ctx.guild.channels, id=logger_channel)
      embed = discord.Embed(title="**Logged Info**", color=discord.Color.green())
      embed.add_field(name=f"**Ticket :**",
                      value=f"{ctx.channel.name}",
                      inline=True)
      embed.add_field(name="**Action** : **User Added**", value="", inline=True)
      embed.add_field(name=f"User   : {ctx.author.mention}",
                      value="",
                      inline=True)
      embed.add_field(name=f"Added :", value=f"{user.mention}", inline=False)
      embed.set_footer(text="Created & Managed by ECOW")
      await log_channel.send(embed=embed)
      await ctx.send(f"{user.mention} has been added to the battle room!")
    else:
      await ctx.send("You don't have the permission to use this command !")

  @commands.hybrid_command(name="remove",description="Removes member from the ticket")
  async def remove(self, ctx, user: discord.Member):
    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:
      await ctx.send("Role not set for the bot ")
    role_list =   [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [int(role.id) for role in ctx.author.roles]:
      await ctx.channel.set_permissions(user, view_channel=False)
      db = db_handler.SQL_Func()
      s = db.fetch_ticket_setup(ctx.guild.id)
      s = [j for j in s]
      logger_channel = int(s[0][3])
      log_channel = discord.utils.get(ctx.guild.channels, id=logger_channel)
      embed = discord.Embed(title="**Logged Info**", color=discord.Color.green())
      embed.add_field(name=f"**Ticket :**",
                      value=f"{ctx.channel.name}",
                      inline=True)
      embed.add_field(name="**Action** : **User Removed**",
                      value="",
                      inline=True)
      embed.add_field(name=f"User   : {ctx.author.mention}",
                      value="",
                      inline=True)
      embed.add_field(name=f"Removed :", value=f"{user.mention}", inline=False)
      embed.set_footer(text="Created & Managed by ECOW")
      await log_channel.send(embed=embed)
      await ctx.send(f"{user.mention} has been removed from the battle room!")
    else:
      await ctx.send("You dont have the permission to use this command ! ")

  
  @commands.hybrid_command(name="close",description="Close the battle ticket")
  async def close(self, ctx):
    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:
      await ctx.send("Role not set for the bot ")
    role_list =   [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [int(role.id) for role in ctx.author.roles]:
      db = db_handler.SQL_Func()
      s = db.fetch_ticket_setup(ctx.guild.id)
      s = [j for j in s]
      await ctx.send("Channel will be closed in 10 secs")
      import random
      number = random.choices([i for i in range(10000)])
      await ctx.channel.set_permissions(ctx.guild.default_role,
                                        view_channel=False)
      members = ctx.channel.members
  
      for member in members:
        try:
          await ctx.defer()
          await ctx.channel.set_permissions(member, view_channel=False)
        except:
          pass
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
      roles = s[0][-1].split("-")
      roles = [int(i) for i in roles]
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
  
      closed_category = int(s[0][2])
      logger_channel = int(s[0][3])
      log_channel = discord.utils.get(ctx.guild.channels, id=logger_channel)
      closed_category = discord.utils.get(ctx.guild.categories,
                                          id=closed_category)
  
      embed = discord.Embed(title="**Logged Info**", color=discord.Color.blue())
      embed.add_field(name=f"**Ticket** : {ctx.channel.name}",
                      value="",
                      inline=True)
      embed.add_field(name="**Action** : **Closed**", value="", inline=True)
      embed.add_field(name=f"User   : {ctx.author.mention}",
                      value="",
                      inline=True)
      embed.set_footer(text="Created & Managed by ECOW")
      await ctx.channel.edit(name=ctx.channel.name,
                             category=closed_category,
                             overwrites=overwrites)
      await log_channel.send(embed=embed)
      embed = discord.Embed(
          title=
          f"{ctx.channel.mention} was closed successfully by {ctx.author.mention}",
          color=discord.Color.red())
      await ctx.send(embed=embed)
    else:
      await ctx.send("You don't have the permission to use this command !")

  @commands.hybrid_command(name="reopen",description="Re-opens the ticket")
  async def reopen(self, ctx):
    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:
      await ctx.send("Role not set for the bot ")
    role_list =   [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [int(role.id) for role in ctx.author.roles]:
      db = db_handler.SQL_Func()
      s = db.fetch_ticket_setup(ctx.guild.id)
      s = [j for j in s]
      logger_channel = int(s[0][3])
      log_channel = discord.utils.get(ctx.guild.channels, id=logger_channel)
      open_cat = int(s[0][1])
      open_cat = discord.utils.get(ctx.guild.channels, id=open_cat)
  
      await ctx.channel.edit(category=open_cat)
      embed = discord.Embed(
          title=f"Channel Re-opened by {ctx.author.mention} Successfully !",
          description="",
          color=discord.Color.green())
      await ctx.send(embed=embed)
  
      embed = discord.Embed(title="**Logged Info**", color=discord.Color.blue())
      embed.add_field(name=f"**Ticket :**",
                      value=f"{ctx.channel.name}",
                      inline=True)
      embed.add_field(name="**Action** : **Channel Re-Opened**",
                      value="",
                      inline=True)
      embed.add_field(name=f"User   : {ctx.author.mention}",
                      value="",
                      inline=True)
      embed.set_footer(text="Created & Managed by ECOW")
      await log_channel.send(embed=embed)
    else:
      await ctx.send("You don't have the permission to use this command !")
      
  @commands.hybrid_command(name="clear_ticket_setup",description="Clears the pannel setup")
  async def clear_ticket_setup(self, ctx):
    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:
      await ctx.send("Role not set for the bot ")
    role_list =   [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [int(role.id) for role in ctx.author.roles]:
      db = db_handler.SQL_Func()
      s = db.fetch_ticket_setup(ctx.guild.id)
      s = [j for j in s]
      logger_channel = int(s[0][3])
      log_channel = discord.utils.get(ctx.guild.channels, id=logger_channel)
  
      embed = discord.Embed(title="**Logged Info**",
                            color=discord.Color.dark_red())
      embed.add_field(name=f"**Ticket :**",
                      value=f"{ctx.channel.name}",
                      inline=True)
      embed.add_field(name="**Action** : **SETUP CLEARED**",
                      value="",
                      inline=True)
      embed.add_field(name=f"User   : {ctx.author.mention}",
                      value="",
                      inline=True)
      embed.set_footer(text="Created & Managed by ECOW")
      await log_channel.send(embed=embed)
      db = db_handler.SQL_Func()
      db.drop_ticket_setup()
      await ctx.send('Ticket setup has been cleared!')
    else:
      await ctx.send("You don't have the permission to use this command ! ")

  @commands.hybrid_command(name="transcript",description="Generates transcript for the ticket")
  async def transcript(self, ctx: commands.Context):
    
    await ctx.defer()
    self.db = db_handler.SQL_Func()
    self.challonge_supervisor = []
    self.challonge_supervisor.append(self.db.fetch_challonge_role_id())
    try:
      self.challonge_supervisor = int(self.challonge_supervisor[0][0][0])
    except:
      await ctx.send("Role not set for the bot ")
    role_list =   [role.id for role in ctx.author.roles]
    if int(self.challonge_supervisor) in [int(role.id) for role in ctx.author.roles]:
      db = db_handler.SQL_Func()
      s = db.fetch_ticket_setup(ctx.guild.id)
      s = [j for j in s]
      transcript_channel = int(s[0][4])
      log_channel = int(s[0][3])
      trans_channel = discord.utils.get(ctx.guild.channels,
                                        id=transcript_channel)
      log_channel = discord.utils.get(ctx.guild.channels, id=log_channel)
  
      transcript = await chat_exporter.export(ctx.channel)
  
      if transcript is None:
        return
  
      transcript_file = discord.File(
          io.BytesIO(transcript.encode()),
          filename=f"transcript-{ctx.channel.name}.html",
      )
      message = await trans_channel.send(file=transcript_file)
      link = await chat_exporter.link(message)
      embed = discord.Embed(title="**Logged Info**", color=discord.Color.blue())
      embed.add_field(name=f"**Ticket :**",
                      value=f"{ctx.channel.name}",
                      inline=True)
      embed.add_field(name="**Action** : **Transcript Generated**",
                      value="",
                      inline=True)
      embed.add_field(name=f"User   : {ctx.author.mention}",
                      value="",
                      inline=True)
      embed.add_field(name=f"Transcript :",
                      value=f"[Direct-Link]({link})",
                      inline=False)
      embed.set_footer(text="Created & Managed by ECOW")
      await log_channel.send(embed=embed)
      await trans_channel.send(embed=embed)
      embed = discord.Embed(
          title=f"Transcript generated  for the channel successfully!")
      await ctx.send(embed=embed)
    else:
      await ctx.send("You don't have the permission to use this command ! ")






# Add the cog to the bot
async def setup(bot):
  await bot.add_cog(Ticket(bot))
