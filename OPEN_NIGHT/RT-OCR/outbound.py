from rich import print

import pip
import datetime
import time

class Outbound:

    def __init__(self, is_debug : bool, is_server : bool):

        self.is_debug = is_debug
        self.is_server = is_server

    def get_timestamp(self):
        raw_timestamp = time.time()
        timestamp = datetime.datetime.fromtimestamp(raw_timestamp).strftime('[%H:%M:%S]')
        return timestamp

    def log(self, state : str, context : str, speaker = None): # white
        print(f"[bold yellow]{self.get_timestamp()}[/bold yellow] [bold blue]:[/bold blue] ({state}/LOG) -> {context}")

    def warn(self, state : str, context : str, speaker = None): # orange
        print(f"[bold yellow]{self.get_timestamp()}[/bold yellow] [bold blue]:[/bold blue] [bold orange3]({state}/WARN) -> {context}[/bold orange3]")

    def error(self, state : str, context : str, speaker = None): # red
        print(f"[bold yellow]{self.get_timestamp()}[/bold yellow] [bold blue]:[/bold blue] [bold red]({state}/ERROR) -> {context}[/bold red]")

    def success(self, state : str,  context : str, speaker = None): # green
        print(f"[bold yellow]{self.get_timestamp()}[/bold yellow] [bold blue]:[/bold blue] [bold green]({state}/SUCCESS) -> {context}[/bold green]")