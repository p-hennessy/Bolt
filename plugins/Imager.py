"""
    Description:
        Ask bot for images from Google Image search API!

    Contributors:
        - Patrick Hennessy
"""
from arcbot import Plugin
from arcbot import command
from arcbot.utils import Colors
from arcbot.utils import Timer
from arcbot.utils import cache

import random
import requests

secrets = {
    "cx": "",
    "key": ""
}

class Imager(Plugin):
    @command("^image (.+)$", access=100)
    def google(self, event):
        with Timer() as timer:
            query = event.arguments[1]
            images = self.search_google(query)
            image_url = random.choice(images)['link']

            embed = {
                "title": f":camera: {query}",
                "url": image_url,
                "image": {"url": image_url, "proxy_url": image_url},
                "footer": {"text": f"⏰ {timer.delta}ms | 🔌 Imager.google"}
            }

            self.say(event.channel_id, embed=embed)

    @cache(60*60)
    def search_google(self, query):
        url = "https://cse.google.com:443/cse/publicurl"
        params = {
            "q": query,
            "searchType": "image",
            "fields": "items(link)",
            "cx": secrets['cx'],
            "key": secrets['key']
        }

        response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
        response.raise_for_status()

        images = response.json()['items']
        return images
