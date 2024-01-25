import mysql.connector
import chat_exporter
import sqlite3

class SQL_Func:

  #-----------Database Initialization :
  def __init__(self):
    self.create_tournament_table()
    self.create_tournament_players()
    self.create_tournament_matches()
    self.challonge_log_table()
    self.challonge_result_table()
    self.challonge_testing_table()
    self.challonge_super()
    self.ticket_setup()

#--------------------------DB Initiazation Functions :

  def connect(self):
    #self.conn =  sqlite3.connect('ECOW_TOURS.sqlite')
    
    self.conn = mysql.connector.connect(
        host="sql12.freesqldatabase.com",
        user="sql12675402",
        password="ugVaKPkg57",
        database="sql12675402"
     )
    self.cur = self.conn.cursor(buffered=True)


  def commit(self):
    self.conn.commit()

  def close(self):
    self.conn.close()

  def execute(self, querry, args=""):
    self.cur.execute(querry, args)
    self.commit()
    return True

#------------DROP DATA

  def drop_ticket_setup(self):
    self.connect()
    querry = '''DROP TABLE ECOW_TICKET_SETUP'''
    self.execute(querry)
    self.commit()
    self.close()
    self.ticket_setup()

  def drop_tournament_matches(self):

    self.connect()
    querry = '''DROP TABLE ECOW_MATCHES'''
    self.execute(querry)
    self.commit()
    self.close()

  def drop_tournament_players(self):

    self.connect()
    querry = '''DROP TABLE ECOW_PLAYERS'''
    self.execute(querry)
    self.commit()
    self.close()

  def drop_tournament(self):
    self.connect()
    querry = '''DROP TABLE ECOW_TOURS'''
    self.execute(querry)
    self.commit()
    self.close()

  def clear_config(self):
    self.connect()
    querry = '''DROP TABLE  ECOW_CHALLONGE_LOG'''
    self.execute(querry)
    self.commit()
    querry = '''DROP TABLE ECOW_CHALLONGE_RESULT'''
    self.execute(querry)
    self.commit()
    querry = '''DROP TABLE ECOW_CHALLONGE_TESTING'''
    self.execute(querry)
    self.commit()
    querry = '''DROP TABLE ECOW_CHALLONGE_ROLE'''
    self.execute(querry)
    self.commit()
    self.close()
    self.challonge_super()
    self.challonge_log_table()
    self.challonge_result_table()
    self.challonge_testing_table()

#-----------Creating Tour Tables :

  def challonge_super(self):
    self.connect()
    querry = '''CREATE TABLE IF NOT EXISTS ECOW_CHALLONGE_ROLE(ROLE_ID VARCHAR(200))'''
    self.execute(querry)
    self.commit()
    self.close()
    print("CHALLONGE ROLE TABLE CREATED")

  def challonge_log_table(self):
    self.connect()
    querry = '''CREATE TABLE IF NOT EXISTS ECOW_CHALLONGE_LOG(CHANNEL_ID VARCHAR(200),CHANNEL_NAME VARCHAR(200),GUILD_ID VARCHAR(200))'''
    self.execute(querry)
    self.commit()
    self.close()
    print("CHALLONGE LOG TABLE CREATED")

  def challonge_testing_table(self):
    self.connect()
    querry = '''CREATE TABLE  IF NOT EXISTS ECOW_CHALLONGE_TESTING(CHANNEL_ID VARCHAR(200),CHANNEL_NAME VARCHAR(200),GUILD_ID VARCHAR(200))'''
    self.execute(querry)
    self.commit()
    self.close()
    print("CHALLONGE TEST TABLE CREATED")

  def challonge_result_table(self):
    self.connect()
    querry = '''CREATE TABLE IF NOT EXISTS ECOW_CHALLONGE_RESULT(CHANNEL_ID VARCHAR(200),CHANNEL_NAME VARCHAR(200),GUILD_ID VARCHAR(200))'''
    self.execute(querry)
    self.commit()
    self.close()
    print("CHALLONGE RESULT TABLE CREATED")

  def create_tournament_table(self):
    self.connect()
    querry = '''CREATE TABLE IF NOT EXISTS ECOW_TOURS(Tour_Id VARCHAR(200),
       Tour_Name VARCHAR(200),Tour_Type VARCHAR(200),Tour_Bracket VARCHAR(200),
       Participant_Count VARCHAR(200),UNIQUE(Tour_Id));'''
    self.execute(querry)
    self.commit()
    self.close()
    print(" TOUR TABLE CREATED !")

  def create_tournament_matches(self):
    self.connect()
    querry = '''CREATE TABLE IF NOT EXISTS ECOW_MATCHES(Match_Name VARCHAR(200),Tournament_Name VARCHAR(200),Tour_Id VARCHAR(200),Match_Id VARCHAR(200),
      Player1_Id VARCHAR(200),Player2_Id VARCHAR(200),Scores VARCHAR(200),Winner VARCHAR(200),State VARCHAR(200),UNIQUE(Match_Id));'''
    self.execute(querry)
    self.commit()
    self.close()
    print(" MATCH TABLE CREATED !")

  def create_tournament_players(self):
    self.connect()
    querry = '''CREATE TABLE IF NOT EXISTS ECOW_PLAYERS(Tour_ID VARCHAR(200),
      Player_Id VARCHAR(200),Player_Main_Id VARCHAR(200),Player_Name VARCHAR(200),UNIQUE(Player_Id));'''
    self.execute(querry)
    self.commit()
    self.close()
    print(" PLAYER TABLE CREATED !")

  def ticket_setup(self):

    self.connect()
    querry = '''CREATE TABLE IF NOT EXISTS ECOW_TICKET_SETUP(GUILD_ID VARCHAR(200),OPEN_ID VARCHAR(200),CLOSE_ID 
VARCHAR(200),LOG_CHANNEL_ID VARCHAR(200),TRANSCRIPT_CHANNEL_ID VARCHAR(200),ROLES_ID VARCHAR(200),UNIQUE(GUILD_ID))'''

    self.execute(querry)
    self.commit()
    self.close()
    print("TICKET SETUP TABLE CREATED !")

#-----------------------DB Insertion Functions :

  def insert_ticket_setup(self, value):
    self.connect()
    querry = '''INSERT INTO ECOW_TICKET_SETUP(GUILD_ID,OPEN_ID,CLOSE_ID,LOG_CHANNEL_ID,TRANSCRIPT_CHANNEL_ID,ROLES_ID) VALUES (%s,%s,%s,%s,%s,%s)'''
    value = (
        value[0],
        value[1],
        value[2],
        value[3],
        value[4],
        value[5],
    )
    try:
      self.execute(querry, value)
    except:
      pass
    self.commit()
    self.close()

  def insert_challonge_role(self, value):
    self.connect()
    querry = '''INSERT INTO ECOW_CHALLONGE_ROLE(ROLE_ID)VALUES(%s)'''
    value = (value, )
    try:
     self.execute(querry, value)
    except:
     pass
    self.commit()
    self.close()
    print("CHALLONGE ROLE INSERTED")

  def insert_log(self, value):
    self.connect()
    querry = '''INSERT INTO ECOW_CHALLONGE_LOG(CHANNEL_ID,CHANNEL_NAME,GUILD_ID) VALUES(%s,%s,%s)'''
    value = (
        value[0],
        value[1],
        value[2],
    )
    try:
      self.execute(querry, value)
    except:
      pass
    self.commit()
    self.close()
    print("CHALLONGE LOG INSERTED")

  def insert_result(self, value):
    self.connect()
    querry = '''INSERT INTO ECOW_CHALLONGE_RESULT(CHANNEL_ID,CHANNEL_NAME,GUILD_ID) VALUES(%s,%s,%s)'''
    value = (
        value[0],
        value[1],
        value[2],
    )
    try:
      self.execute(querry, value)
    except:
      pass
    self.commit()
    self.close()
    print("CHALLONGE RESULT INSERTED")

  def insert_testing(self, value):
    self.connect()
    querry = '''INSERT INTO ECOW_CHALLONGE_TESTING(CHANNEL_ID,CHANNEL_NAME,GUILD_ID) VALUES(%s,%s,%s)'''
    value = (
        value[0],
        value[1],
        value[2],
    )
    try:
      self.execute(querry, value)
    except:
      pass
    self.commit()
    self.close()
    print("CHALLONGE TESTING INSERTED")

  def insert_tournament(self, value):
    self.connect()
    querry = '''INSERT INTO ECOW_TOURS(Tour_Id,Tour_Name,Tour_Type,
      Tour_Bracket,Participant_Count) VALUES(%s,%s,%s,%s,%s)'''
    try:
      for i in range(len(value)):
        self.execute(querry, value[i])
    except:
      pass
    self.commit()
    self.close()
    print("CHALLONGE TOUR INSERTED")

  def insert_tournament_players(self, value):
    self.connect()
    querry = '''INSERT INTO ECOW_PLAYERS(Tour_ID,Player_Id,Player_Main_Id,Player_Name)VALUES(%s,%s,%s,%s)'''
    try:
      for i in range(len(value)):
        self.execute(querry, value[i])
    except:
      pass

    self.commit()
    self.close()
    print("CHALLONGE PLAYER INSERTED")

  def insert_tournament_matches(self, value):
    self.connect()
    querry = '''INSERT INTO ECOW_MATCHES(Match_Name,Tournament_Name,Tour_Id ,Match_Id ,Player1_ID,Player2_Id,Scores,Winner,State)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    try:
      for i in range(len(value)):
        self.execute(querry, value[i])

    except:
      pass
    self.commit()
    self.close()
    print("CHALLONGE MATCHES INSERTED")


#-------------------------------FETCH FROM DB:

# fetch all players of a tournament by tournament id

  def fetch_ticket_setup(self, value):
    self.connect()
    value = (value, )
    querry = '''SELECT * FROM ECOW_TICKET_SETUP WHERE GUILD_ID = %s'''
    self.execute(querry, value)
    k = self.cur.fetchall()
    k = [i for i in k]
    self.commit()
    self.close()
    return k

  def fetch_challonge_role_id(self):
    self.connect()
    querry = '''SELECT ROLE_ID FROM ECOW_CHALLONGE_ROLE'''
    self.execute(querry)
    s = self.cur.fetchall()
    self.commit()
    self.close()
    return s

  def fetch_log_channelid(self):
    self.connect()
    querry = '''SELECT CHANNEL_ID FROM ECOW_CHALLONGE_LOG'''
    self.execute(querry)
    s = self.cur.fetchall()
    self.commit()
    self.close()
    return s

  def fetch_result_channelid(self):
    self.connect()
    querry = '''SELECT CHANNEL_ID FROM ECOW_CHALLONGE_RESULT'''
    self.execute(querry)
    s = self.cur.fetchall()
    self.commit()
    self.close()
    return s

  def fetch_testing_channelid(self):
    self.connect()
    querry = '''SELECT CHANNEL_ID FROM ECOW_CHALLONGE_TESTING'''
    self.execute(querry)
    s = self.cur.fetchall()
    self.commit()
    self.close()
    return s

  def fetch_all_players(self, value):
    self.connect()
    value = (value, )
    querry = '''SELECT * FROM ECOW_PLAYERS WHERE Tour_ID = %s'''
    self.execute(querry, value)
    m = []
    for i in self.cur.fetchall():
      m.append(i)

    self.commit()
    self.close()
    return m

  # fetch all pending matches of all tournament
  def fetch_all_matches(self):
    self.connect()
    querry = '''SELECT * FROM ECOW_MATCHES WHERE State = "pending" OR State = "open"'''
    self.execute(querry)
    m = []
    for i in self.cur.fetchall():
      m.append(i)
    self.commit()
    self.close()
    return m

  # fetch all tournaments of ECOW
  def fetch_all_tournaments(self):
    self.connect()
    querry = '''SELECT * FROM ECOW_TOURS'''
    self.execute(querry)
    m = []
    for i in self.cur.fetchall():
      m.append(i)
    self.commit()
    self.close()
    return m

  # fetch info  of one given tournament by tournament id
  def fetch_one_tournament(self, value):
    self.connect()
    value = (value, )
    querry = '''SELECT * FROM ECOW_TOURS WHERE Tour_Name = %s'''
    self.execute(querry, value)
    m = []
    for i in self.cur.fetchall():
      m.append(i)
    self.commit()
    self.close()
    return m

  def fetch_one_tournament_id(self, value):
    self.connect()
    value = (value, )
    querry = '''SELECT * FROM ECOW_MATCHES WHERE Match_Name = %s'''
    self.execute(querry, value)
    m = []
    for i in self.cur.fetchall():
      m.append(i)
    self.commit()
    self.close()
    return m

  # fetch info of one player by player id
  def fetch_one_player(self, value):
    self.connect()
    value = (
        value,
        value,
    )
    querry = '''SELECT * FROM ECOW_PLAYERS WHERE Player_ID = %s OR Player_Main_Id = %s'''
    self.execute(querry, value)
    m = []
    for i in self.cur.fetchall():
      m.append(i)

    self.commit()
    self.close()
    return m

  def fetch_one_player_name(self, value):
    self.connect()
    value = (value, )
    querry = '''SELECT Player_ID,Player_Main_ID FROM ECOW_PLAYERS WHERE Player_Name = %s'''
    self.execute(querry, value)
    m = []
    for i in self.cur.fetchall():
      m.append(i)

    self.commit()
    self.close()
    return m

  # fetch info of one match by tour id & match no
  def fetch_one_match(self, value):
    self.connect()
    value = (value, )
    querry = '''SELECT * FROM ECOW_MATCHES WHERE Match_Name = %s'''
    self.execute(querry, value)
    m = []
    for i in self.cur.fetchall():
      m.append(i[1])

    self.commit()
    self.close()
    return m

  def fetch_one_match_id(self, value):
    self.connect()
    value = (value, )
    querry = '''SELECT * FROM ECOW_MATCHES WHERE Match_Name = %s'''
    self.execute(querry, value)
    m = []
    for i in self.cur.fetchall():
      m.append(i[3])

    self.commit()
    self.close()
    return m
