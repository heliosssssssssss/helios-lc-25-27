import requests
from pprint import pprint
import json

uri = "https://hisc.life/api/"

rq = requests.get(f"{uri}get-post-list")
pprint(rq.json())
