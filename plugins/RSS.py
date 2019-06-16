"""
    Description:
        Watches and posts in channels with RSS feeds.

    Contributors:
        - Patrick Hennessy
"""
from bolt import Plugin
from bolt import interval
from bolt import parse_command
from bolt.utils import Timer
import feedparser
import html2text
import time
import datetime
import gevent

class RSS(Plugin):
    def activate(self):
        self.feed_url = "http://www.teamfortress.com/rss.xml"
        self.last_checked = time.gmtime()
        self.feeds = self.database.feed_channels

    @parse_command("feed {onoff}")
    def feed(self, event):
        args, kwargs = event.arguments
        toggle_status = kwargs['onoff']

        tf2_feed = self.feeds.find_one({"feed_url": self.feed_url})
        channel_id = event.message.channel_id

        if toggle_status == "on":
            if not tf2_feed:
                self.feeds.insert_one({"feed_url": self.feed_url, "channels": [channel_id]})
                self.say(channel_id, f"Subcribed this channel for updates to {self.feed_url}")
                return
            else:
                for channel in tf2_feed['channels']:
                    if channel == channel_id:
                        self.say(channel_id, f"This channel is already subcribed to {self.feed_url}")
                        break
                else:
                    self.feeds.update_one({"feed_url": self.feed_url}, {"$push": {"channels": channel_id}})
                    self.say(channel_id, f"Subcribed this channel for updates to {self.feed_url}")

        elif toggle_status == "off":
            if not tf2_feed:
                self.say(channel_id, f"I dont have any channels listed for {self.feed_url}")
            else:
                self.feeds.update_one({"feed_url": self.feed_url}, {"$pull": {"channels": channel_id}})
                self.say(channel_id, f"Unsubcribed this channel for updates to {self.feed_url}")

    @interval(60)
    def update(self):
        tf2_feed = self.feeds.find_one({"feed_url": self.feed_url})

        if not tf2_feed or not tf2_feed['channels']:
            return

        with Timer() as timer:
            # Get feed
            parsed_feed = feedparser.parse(self.feed_url)
            h = html2text.HTML2Text()
            h.ignore_images = True
            h.ignore_tables = True

            # Check last updated time
            last_checked = self.last_checked

            try:
                if last_checked > parsed_feed.feed['updated_parsed']:
                    return
            except KeyError:
                if last_checked > parsed_feed.updated_parsed:
                    return

            for post in parsed_feed.entries:
                # Ensure we're going to post something new
                if last_checked < post['published_parsed']:
                    summary = h.handle(post.summary)
                    summary = summary[:256]
                    timestamp = time.strftime("%a, %b %d %Y @ %I:%M %p", post['published_parsed'])

                    embed =  {
                        "title": f"__{post.title}__",
                        "url": f"{post.link}",
                        "author": {
                            "name": "Team Fortress 2 Updates",
                            "icon_url": "http://icons.iconarchive.com/icons/sicons/basic-round-social/512/rss-icon.png"
                        },
                        "description": f"*{timestamp}*\n\n{summary}",
                        "footer": {
                          "text": f"⏰ {timer.delta}ms | 🔌 RSS"
                        }
                    }

                    for channel in tf2_feed['channels']:
                        self.say(channel, embed=embed)
                        gevent.sleep(1)

                    self.last_checked = time.gmtime()
                    break
