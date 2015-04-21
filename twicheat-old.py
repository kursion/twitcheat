import shutil
import requests
import subprocess
import json
import sys
import threading
import time
import queue


startTime = time.time()
concurrent = 25


class Twicheat:
    CURRENT_TID = 0
    BIN = {
        'livestreamer': None,
    }
    VERSION = 0.1
    STREAMER = "kursion"

    CONFIG = {
        'nbrViewers': int(sys.argv[1]),
        'nbrThreads': int(sys.argv[2]),
        'concurrent': 25
    }

    Q = queue.Queue(
        maxsize=CONFIG["concurrent"]*2)  # *2 is a convention

    NBR_SOCKETS = 0
    URLS = []
    URLS_USED = []

    def __init__(self, STREAMER=None):
        self.STREAMER = self.STREAMER if not STREAMER else STREAMER
        print("Welcome to Twicheat", self.STREAMER,
              "v" + str(self.VERSION))
        self.getToken()
        # self.initCheck()
        # self.run()

    def getToken():


    def initCheck(self):
        self.BIN["livestreamer"] = shutil.which("livestreamer")
        if not self.BIN["livestreamer"]:
            print("You should have livestream installed !",
                  "You can find it here:",
                  "https://github.com/chrippa/livestreamer/")
            sys.exit(1)

    def run(self):
        # Building sockets
        for i in range(0, self.CONFIG["nbrThreads"]):
            threading.Thread(target=self.build).start()

        # Wait until sockets are built
        while (self.CONFIG["nbrViewers"] != self.NBR_SOCKETS):
            time.sleep(1)

        # Consuming the items
        for i in range(self.CONFIG["concurrent"]):
            try:
                t = threading.Thread(target=self.view)
                t.daemon = True
                t.start()
            except:
                print('thread error')

        while True:
            try:
                for url in self.URLS:
                    self.Q.put(url.strip())
                self.Q.join()
            except KeyboardInterrupt:
                    sys.exit(1)

    def build(self):
        """ Building the threads """
        self.CURRENT_TID += 1
        TID = self.CURRENT_TID
        print("Building", TID)
        while True:
            if self.NBR_SOCKETS < self.CONFIG["nbrViewers"]:
                self.NBR_SOCKETS += 1
                print(TID, "Building viewers", str(self.NBR_SOCKETS) +
                      "/" + str(self.CONFIG["nbrViewers"]))
                u = self.getURL()
                if u:
                    print("Adding new url", self.NBR_SOCKETS)
                    self.URLS.append(u)
            else:
                print(TID, "Numbers of viewers reached:",
                      self.CONFIG["nbrViewers"])
                break

    def view(self):
        while True:
            url = self.Q.get()
            print("Starting view")
            requests.head(url)
            if (url in self.URLS_USED):
                print("Got url used !")
                self.URLS.remove(url)
                self.URLS_USED.remove(url)
                self.NBR_SOCKETS -= 1
            else:
                print("Got url !")
                self.URLS_USED.append(url)
            self.Q.task_done()

    def getURL(self):  # Get tokens
        output = subprocess.Popen(["livestreamer",
                                   "twitch.tv/"+self.STREAMER, "-j"],
                                  stdout=subprocess.PIPE).communicate()[0]
        outputUTF8 = output.decode("utf-8")
        # Parse json and return the URL parameter
        outputJSON = json.loads(outputUTF8)
        if "error" in outputJSON:
            print("Error while building URL:", outputJSON["error"])
        else:
            return json.loads(outputUTF8)['streams']['worst']['url']


tc = Twicheat("GOD_BATLE")
