from cogs.Challonges import api
import requests
import json

headers = {
    'User-Agent':
    'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)'
}


def show(tournament_id, show_participants=0, show_matches=0):

  session = requests.Session()
  username, password = api.my_key()
  print(username, password)
  session.auth = (username, password)
  auth = session.post(api.CHALLONGE_API_URL)
  url = f"{api.CHALLONGE_API_URL}/v1/tournaments/{tournament_id}.json?include_matches={show_matches}&include_participants={show_participants}"
  response = session.get(url, headers=headers)
  #print(response.text)
  result = json.loads(response.text)
  return result
