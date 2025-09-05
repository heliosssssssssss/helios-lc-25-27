import time 
import requests 
import json
from multiprocessing.pool import ThreadPool as Pool

uri = "https://hisc.life/api"

def send():
    rq = requests.get(url=f"{uri}/get-post-list")
    print(f"[OUTBOUND -> {uri}/get-post-list | INBOUND -> STATUS_CODE => {rq.status_code}]")


while True:
    send()