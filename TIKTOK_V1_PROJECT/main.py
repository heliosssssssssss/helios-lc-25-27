import time
import random
from rich.console import Console
from rich import print

console = Console()

## DOCS

## lyrics = [ [lyric_text, time_to_complete], [etc..] ]
## required: time, random, rich 
## if time_to_complete is not included in a lyric, it will set to default_delay
## text in [] is colored based upon random select 

## a side project by @heliosdagoat 
## repo is open to issues/pull-requests
## thanks for watching my video too btw :)

##

lyrics = [
    ["standing here [alone] now", 1.6],
    ["think that [we] could drive around", 1.7],
    ["i just wanna say how [i love you] with your hair down", 3.75],
    ["[baby] you dont gotta fight", 2],
    ["i'll be here till the [end of time]", 1.8],
    ["wishing that you were [mine]", 1.65],
    ["[pull you in] it's alright", 1.5]
]

colors = [
    "bright_red", "bright_green", "bright_blue", "bright_cyan", "bright_magenta", "bright_yellow"
]

default_delay = 0.2

print()
print()

print("made by [bright_red]@heliosdagoat[/]")
print("open source: [bright_cyan]https://helios2.pro/lyric-printer[/]")

print()
print()

for obj in lyrics:
    line = obj[0]
    delay = obj[1] if len(obj) > 1 else default_delay

    total_chars = len(line.replace("[", "").replace("]", ""))
    char_delay = delay / max(total_chars, 1)

    i = 0
    in_color = False
    color = None
    prev_color = None

    while i < len(line):
        char = line[i]

        if char == "[":
            in_color = True
            available = [c for c in colors if c != prev_color]
            color = random.choice(available)
            prev_color = color
            i += 1
            continue
        elif char == "]":
            in_color = False
            color = None
            i += 1
            continue

        if in_color and color:
            console.print(f"[{color}]{char}[/]", end="", soft_wrap=True)
        else:
            console.print(char, end="", soft_wrap=True)

        time.sleep(char_delay)
        i += 1

    print()

input()