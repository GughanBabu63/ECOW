import json
from sqlite3 import complete_statement
from discord.ext.commands import bot
import requests


class Challonge_func:

  def __init__(self):
    self.user_name = "Rayleigh63"
    self.api_key   = "yap4bTPYqHDaiKI3ZOb1m6qXJrvfRaZYwbPIvqgu"

  def get_tournament(self, tournament_id):
    session = requests.Session()
    session.auth = (self.user_name, self.api_key)
    auth = session.post('https://api.challonge.com')
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)'
    }
    url = f"https://api.challonge.com/v1/tournaments/{tournament_id}.json?include_matches=1"
    response = session.get(url, headers=headers)
    print(response.text)
    result = json.loads(response.text)
    rex = []
    print(type(result))

    tournament_name = result['tournament']['name']
    tournament_id = result['tournament']['id']
    tournament_url = "https://challonge.com/" + result['tournament']['url']
    tournament_type = result['tournament']['tournament_type']
    tournament_state = result['tournament']['state']
    tournament_start = result['tournament']['started_at']
    tournament_end = result['tournament']['completed_at']
    tournament_participants = result['tournament']['participants_count']
    rex.append((tournament_id, tournament_name, tournament_type,
                tournament_url, tournament_participants))
    return rex

  def get_all_participants(self, tournament_id):
    tournament_id = tournament_id[0]
    session = requests.Session()
    session.auth = (self.user_name, self.api_key)
    auth = session.post('https://api.challonge.com')
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)'
    }
    url = f"https://api.challonge.com/v1/tournaments/{tournament_id}/participants.json"
    response = session.get(url, headers=headers)
    result = json.loads(response.text)
    rex = []
    print(result)
    for i in range(len(result)):
       try: 
        participant_id = result[i]['participant']['group_player_ids'][0]
       except:
        participant_id = result[i]['participant']['id']
       participant_main_id = result[i]['participant']['id']
       participant_name = result[i]['participant']['name']
       tournament_id = result[i]['participant']['tournament_id']
       rex.append((tournament_id, participant_id, participant_main_id,participant_name))
    return rex

  def get_all_matches(self, tournament_id):
    tournament_id = tournament_id[0]
    session = requests.Session()
    session.auth = (self.user_name, self.api_key)
    auth = session.post('https://api.challonge.com')
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)'
    }
    url = f"https://api.challonge.com/v1/tournaments/{tournament_id}/matches.json"
    response = session.get(url, headers=headers)
    result = json.loads(response.text)
    rex = []
    print(result)
    for i in range(len(result)):
      match_id = result[i]['match']['id']
      tournament_id = result[i]['match']['tournament_id']
      player1_id = result[i]['match']['player1_id']
      player2_id = result[i]['match']['player2_id']
      winner = result[i]['match']['winner_id']
      scores = result[i]['match']['scores_csv']
      state = result[i]['match']['state']
      rex.append((tournament_id, match_id, player1_id, player2_id, scores,
                  winner, state))
    return rex

  def update_score(self, value):

    def updates_score(value):
      session = requests.Session()
      session.auth = (self.user_name, self.api_key)
      auth = session.post('https://api.challonge.com')

      headers = {
          'User-Agent':
          'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)'
      }
      tournament = value[0]
      match = value[1]
      winner = value[2]
      score = value[3]
      params = {
          "match[scores_csv]": f"{score}",
          "match[winner_id]": f"{winner}"
      }
      url = f"https://api.challonge.com/v1/tournaments/{tournament}/matches/{match}.json"
      response = session.put(url, headers=headers, params=params)
      print(response.status_code)
      if str(response.status_code) == "200":
        result = json.loads(response.text)
        return result
      else:
        return None

    result = ""

    result = updates_score(value[0])
    if result == None:
      result = updates_score(value[1])
    rex = []

    match_id = result['match']['id']
    tournament_id = result['match']['tournament_id']
    player1_id = result['match']['player1_id']
    player2_id = result['match']['player2_id']
    winner = result['match']['winner_id']
    scores = result['match']['scores_csv']
    state = result['match']['state']
    rex.append((tournament_id, match_id, player1_id, player2_id, scores,
                winner, state))
    return rex

  def get_all_tournament(self):

    session = requests.Session()
    session.auth = (self.user_name, self.api_key)
    auth = session.post('https://api.challonge.com')
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)'
    }
    url = f"https://api.challonge.com/v1/tournaments.json"
    response = session.get(url, headers=headers)
    result = json.loads(response.text)
    rex = []
    print(result)
    for i in range(len(result)):
      if "underway" in result[i]['tournament']['state']:
        tour_id = result[i]['tournament']['id']
        tour_name = result[i]['tournament']['name']
        tour_desc = result[i]['tournament']['description']
        if tour_desc == "":
          tour_desc = None

        tour_url = "https://challonge.com/" + result[i]['tournament']['url']
        tour_type = result[i]['tournament']['tournament_type']
        tour_start = result[i]['tournament']["started_at"]
        tour_end = result[i]['tournament']["completed_at"]
        tour_state = result[i]['tournament']["state"]
        tour_game = result[i]['tournament']["game_name"]
        tour_p_co = result[i]['tournament']["participants_count"]
        rex.append((tour_id, tour_name, tour_type, tour_url, tour_p_co))
    return rex
