import json
import sys
import requests

CHALLONGE_API_URL = "https://api.challonge.com"

credential = {"username": None, "api_key": None}


def launch(username, key):

  credential['username'] = username
  credential['api_key'] = key


def my_key():
  return credential['username'], credential['api_key']
