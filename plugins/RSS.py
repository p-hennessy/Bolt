"""
    Description:
        Watches and posts in channels with RSS feeds.

    Contributors:
        - Patrick Hennessy
"""
from arcbot import Plugin
from arcbot import interval
from arcbot import Colors
from arcbot.utils import Timer
import feedparser
import html2text
import time
import datetime

class RSS(Plugin):
    def activate(self):
        test = datetime.datetime.now() - datetime.timedelta(days=10)
        test = test.timetuple()

        self.feeds = [
            {
                "url": "http://www.teamfortress.com/rss.xml",
                "channel": "95672708418768896",
                "last_checked": time.gmtime()
            },
            {
                "url": "https://github.com/blog/broadcasts.atom",
                "channel": "136539488280248320",
                "last_checked": time.gmtime()
            },
            {
                "url": "https://github.com/blog.atom",
                "channel": "136539488280248320",
                "last_checked": time.gmtime()
            }
        ]

    @interval(60)
    def update(self):
        for feed in self.feeds:
            with Timer() as timer:
                # Get feed
                parsed_feed = feedparser.parse(feed['url'])
                h = html2text.HTML2Text()
                h.ignore_images = True
                h.ignore_tables = True

                # Check last updated time
                last_checked = feed['last_checked']

                try:
                    if last_checked > parsed_feed.feed['updated_parsed']:
                        continue
                except KeyError:
                    if last_checked > parsed_feed.updated_parsed:
                        continue

                for post in parsed_feed.entries:
                    # Ensure we're going to post something new
                    if last_checked < post['published_parsed']:
                        summary = h.handle(post.summary)
                        summary = summary[:256]
                        timestamp = time.strftime("%a, %b %d %Y @ %I:%M %p", post['published_parsed'])

                        embed =  {
                            "title": f":satellite: {post.title}",
                            "description": f"**{post.link}**\n*{timestamp}*\n\n{summary}",
                            "footer": {
                              "text": f"⏰ {timer.delta}ms | 🔌 RSS"
                            }
                        }

                        # Post single thing from last update
                        self.say(feed['channel'], embed=embed)
                        feed['last_checked'] = time.gmtime()

                        break
