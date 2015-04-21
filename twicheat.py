import json
import sys
import random
import urllib.request
import subprocess
import re


def getPlaylist(channel):
    queryToken = urllib.request.urlopen(
        "http://api.twitch.tv/api/channels/" +
        "{:s}/access_token".format(channel))
    responseUTF8 = queryToken.read().decode("utf-8")
    queryTokenJSON = json.loads(responseUTF8)

    token = queryTokenJSON["token"]
    sig = queryTokenJSON["sig"]
    url = "http://usher.twitch.tv/api/channel/hls/{channel}.m3u8?" \
        "player=twitchweb&token={token}&sig={sig}&" \
        "allow_audio_only=true&allow_source=true&type=any&p={random}".format(
            channel=channel,
            token=token,
            sig=sig,
            random=random.randrange(1, 100000)
        )
    try:
        queryPlaylist = urllib.request.urlopen(url)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            print("Not streaming")
            sys.exit(1)
        else:
            raise

    responseUTF8 = queryPlaylist.read().decode("utf-8")
    return responseUTF8


def parseM3U8(playlist):
    lines = playlist.split("\n")
    links = {}
    for i, line in enumerate(lines):
        if not line.startswith("#EXT-X-STREAM-INF"):
            continue
        matches = re.findall(r'VIDEO=\"(.+?)\"', line)
        links[matches[0]] = lines[i+1]
    return links


CHANNEL = "y0nd"
playlist = getPlaylist(CHANNEL)

urls = parseM3U8(playlist)
quals = list(urls)
print(quals)

best_qual = quals[0]
worst_qual = quals[-1]
print("Starting in", best_qual)
subprocess.Popen(["vlc", "--qt-minimal-view", urls[best_qual]])
