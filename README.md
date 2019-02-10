![Logo](https://user-images.githubusercontent.com/5940454/29853902-3b4a47dc-8d08-11e7-9158-31874826084c.png)

[![Python](https://img.shields.io/badge/Python-3.6-7289da.svg?style=flat-square)](https://www.python.org/downloads/release/python-360/)
[![License](https://img.shields.io/badge/License-MIT-7289da.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/travis/ns-phennessy/Bolt.svg?style=flat-square)](https://travis-ci.org/ns-phennessy/Bolt)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/01884c4719a746ba8ae317ba10268a44)](https://www.codacy.com/app/ns-phennessy/Bolt?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ns-phennessy/Bolt&amp;utm_campaign=Badge_Grade)


# About Bolt

Bolt is an extensible chatbot written entirely in Python, inspired by
[Errbot](https://github.com/errbotio/errbot) and [Hubot](https://hubot.github.com/) projects.
The goal of this project is to provide a simple to extend bot framework for
[Discord](https://discordapp.com).

Batteries included:
* [Simple command creation](#Command-creation)
* [Hook any event from Discord](#Hook-Discord-Event)
* [Receive data ingress with webhooks](#Webhook)
* [Run code on a set interval](#Code-interval)
* [Schedule code to be run after a time period](#Database-Interaction)
* [Simple database interaction with MongoDB](#Schedule-code-to-run)
* [Intuitive Discord object mapping](#Discord-object-mapping)
* [Bundled in standardized distribution formats](#Installing)

I am open to feedback and suggestions. Feel free to submit a pull request or open an issue :)

Bolt originally started out as a simple Trivia Bot that used long polling and webhooks to read and
write to chat channels. I became obsessed with making this bot more robust and at that time, no bots
existed for Discord, so this bot evolved into a fully vetted framework that I could use to build
functionality off of.

This project is a place I can experiment with design ideas and evolve a sense of personal code
standards. I treat it as an academic project to learn about new libraries and tools available to me
as Python continues to grow.

# Installing

Coming soon...


# Examples

## Command creation
```python
from bolt import Plugin
from bolt import command

class SomePlugin(Plugin):
    @command("hi")
    def on_sayhi(self, event):
        self.say(event.channel_id, f"Hello {event.sender.name}")
```

## Hook Discord Event
```python
from bolt import Plugin
from bolt import subscriber
from bolt.discord import Events

class SomePlugin(Plugin):
    @subscriber(Events.MESSAGE_REACTION_ADD)
    def on_message_reaction_add(self, event):
        # do stuff
```

## Webhook
```python
from bolt import Plugin
from bolt import webhook

class SomePlugin(Plugin):
    @webhook('/hookme', methods=['GET'])
       def webhook(self, request):
           # do stuff
```

## Code interval
```python
from bolt import Plugin
from bolt import interval

class SomePlugin(Plugin):
    @interval(60)
    def updateathing(self, event):
        # do stuff
```

## Database Interaction
```python
from bolt import Plugin
from bolt import command

class SomePlugin(Plugin):
    def activate(self):
        self.users = self.bot.database_client['plugin-users']

    @command("whoami")
    def whoami(self, event):
        author = self.users.find_one({"id": event.author.id})
```

## Schedule code to run
Coming soon...

## Discord object mapping
Coming soon...

# License
Bolt is licensed under the [MIT License](https://github.com/ns-phennessy/Bolt/blob/master/LICENSE.txt)
