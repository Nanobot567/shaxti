#! /bin/python

import json
from sys import stdout
import requests
from time import sleep
import os

import re

HELP = {
    "?/h": "display help",
    "c  ": "open configuration editor",
    "s  ": "search",
    "q  ": "quit",
}

CONFIG_HELP = {
    "a": "add site to config",
    "d": "delete site",
    "e": "edit site",
    "t": "toggle typewrite",
    "q": "exit configuration editor",
    "r": "allow rate limited services",
}

LOGO = r"""
     _                _   _ 
    | |              | | (_)
 ___| |__   __ ___  _| |_ _ 
/ __| '_ \ / _` \ \/ / __| |
\__ \ | | | (_| |>  <| |_| |
|___/_| |_|\__,_/_/\_\\__|_|
                            
"""


def typewrite(text="\n", time=0.003):
    if cfg["settings"]["typewrite"]:
        for char in text:
            stdout.write(char)
            stdout.flush()
            sleep(time)
    else:
        stdout.write(text)


def toBoolean(s):
    if s.lower() == "true":
        return True
    else:
        return False


def toggleSetting(setting):
    if setting in cfg["settings"].keys():
        cfg["settings"][setting] = not cfg["settings"][setting]
    else:
        cfg["settings"][setting] = False

    return str(cfg["settings"][setting])


cfg = {}

if os.path.exists("shaxti.cfg"):
    with open("shaxti.cfg", "r") as f:
        cfg = json.loads(f.read())
else:
    cfg = {"sites": [], "settings": {"typewrite": False, "allow_ratelimit": True}}

typewrite(LOGO)
typewrite("(type h for help)\n")

try:
    while True:
        cmd = input("shxti> ")

        if cmd == "q":
            break
        elif cmd == "?" or cmd == "h":
            for k, v in HELP.items():
                typewrite(f"{k}   {v}\n")
        elif cmd == "s":
            topics = {}

            query = input("shxti/query> ")

            if query != "q" and query != "quit":
                overallIndex = 0

                for index, site in enumerate(cfg["sites"]):
                    response = ""
                    if site["type"] == "discourse":
                        response = requests.get(
                            f"{site['url']}search.json?q={query}"
                        ).json()

                        if "topics" in response.keys():
                            for i, topic in enumerate(response["topics"]):
                                overallIndex += 1

                                typewrite(
                                    f"\n{overallIndex}. [{site['name']}]: {topic['title']} (ID {topic['id']})\n"
                                )

                                typewrite(f"    {response['posts'][i]['blurb']}\n")

                                topics[overallIndex] = [
                                    site["url"],
                                    topic["slug"],
                                    topic["id"],
                                ]

                                if i == 4:
                                    break

                        else:
                            typewrite(
                                f"\n[ERR] no topics found in discourse forum '{site['name']}'\n"
                            )

                        # for i, post in enumerate(response["posts"]):
                        #     typewrite(site['name']+"\n")
                        #     postname = ""
                        #     try:
                        #         postname = post["name"]
                        #     except KeyError:
                        #         try:
                        #             postname = post["username"]
                        #         except KeyError:
                        #             pass

                        #     typewrite(f"{i + 1}. {postname}: {post['blurb']}\n")

                        #     if i == 4:
                        #         break

                    elif site["type"] == "stackexchange":
                        # response = requests.get(f"https://api.stackexchange.com/search/?site={site['url']}&intitle={query}").json()

                        pass

                typewrite("\n")

                cmd = input("shxti/query/number? ")

                topic = topics[int(cmd)]

                response = requests.get(
                    f"{topic[0]}t/{topic[1]}/{topic[2]}.json"
                ).json()

                postindex = 0

                while postindex < len(response["post_stream"]["posts"]):
                    thisPost = response["post_stream"]["posts"][postindex]

                    cookedText = thisPost["cooked"]

                    replaceDict = {
                        "<strong>": "\033[1m",
                        "<h2>": "\033[1m",
                        "</strong>": "\033[22m",
                        "</h2>": "\033[22m",
                        "<p>": "",
                        "<hr>": "",
                        "</hr>": "",
                        "</p>": "",
                        "<em>": "\033[3m",
                        "</em>": "\033[23m",
                        "<code>": "`",
                        "</code>": "`"
                    }

                    for k, v in replaceDict.items():
                        cookedText = cookedText.replace(k, v)

                    cookedText = re.sub(re.compile("<.*?>"), "", cookedText)

                    typewrite(
                        f"\n-- {thisPost['username']} ({thisPost['created_at']}) --\n\n{cookedText}\n\n" 
                    )

                    postindex += 1

                    # cmd = input("shxti/query/post> ")

                    # if cmd == "q":
                    #     break
                    # elif cmd == "n":
                    #     postindex += 1
                    # elif cmd == "p":
                    #     postindex -= 1

                # possibly grab post info from site directly with beautifulsoup
        elif cmd == "c":
            while True:
                cmd = input("shxti/config> ")
                if cmd == "q":
                    break
                elif cmd == "?" or cmd == "h":
                    for k, v in CONFIG_HELP.items():
                        typewrite(f"{k}   {v}\n")
                elif cmd == "a":
                    name = input("shxti/config/addsite/name? ")
                    typ = input("shxti/config/addsite/type? ")
                    url = input("shxti/config/addsite/url? ")
                    rate = toBoolean(input("shxti/config/addsite/ratelimit? "))

                    cfg["sites"].append(
                        {"name": name, "type": typ, "url": url, "rate_limited": rate}
                    )
                elif cmd == "e":
                    for i, v in enumerate(cfg["sites"]):
                        typewrite(str(i) + ". " + str(v) + "\n")
                elif cmd == "d":
                    for i, v in enumerate(cfg["sites"]):
                        typewrite(str(i) + ". " + str(v) + "\n")

                    try:
                        cfg["sites"].pop(int(input("shxti/config/delsite/which? ")))
                    except ValueError:
                        pass
                elif cmd == "t":
                    typewrite("typewrite = " + toggleSetting("typewrite") + "\n")
                elif cmd == "r":
                    typewrite(
                        "allow rate limited services: "
                        + toggleSetting("allow_ratelimit")
                        + "\n"
                    )
                with open("shaxti.cfg", "w+") as f:
                    f.write(json.dumps(cfg))
except KeyboardInterrupt:
    typewrite("\nbye!\n")
