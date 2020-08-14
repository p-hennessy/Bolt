# About

{% hint style="info" %}
This bot is not at a stable state and it's very likely to have breaking changes on a regular basis until the author is happy with it
{% endhint %}

**Bolt** is an extensible chat bot written in Python, inspired by [Errbot](https://github.com/errbotio/errbot) and [Hubot](https://hubot.github.com/) projects. The goal of this project is to provide a simple to extend bot framework for [Discord](https://discordapp.com/).

## **Batteries included:**

{% tabs %}
{% tab title="Commands" %}
```python
from bolt import Plugin
from bolt import command

class Example(Plugin):

    @command("hello")
    def on_hello(self, event):
        event.channel.say(f"Hello {event.sender.name}")
```

For more information, see these pages:

* [Commands](https://github.com/ns-phennessy/Bolt/tree/c236a1f4ad7b8d6b36f52ab6c445e04f51e0d313/docs/plugins/untitled.md)
* [Command Hooks](advanced/command-hooks.md)
{% endtab %}

{% tab title="Interval" %}
```python
from bolt import Plugin
from bolt import interval

class Example(Plugin):

    @interval(60)
    def update_a_thing(self, event):
        # do stuff
```

For more information, see these pages:

* [Interval](plugins/interval.md)
{% endtab %}

{% tab title="Webhooks" %}
```python
from bolt import Plugin
from bolt import webhook

class Example(Plugin):
    
    @webhook('/hookme', methods=['GET'])
       def webhook(self, request):
           # do stuff
```

For more information, see these pages:

* [Webhooks](plugins/webhooks.md)
* [Built-In Webhooks](advanced/built-in-webhooks.md)
{% endtab %}

{% tab title="Discord Events" %}
```python
from bolt import Plugin
from bolt import subscriber
from bolt.discord import Events

class Example(Plugin):

    @subscriber(Events.MESSAGE_REACTION_ADD)
    def on_message_reaction_add(self, event):
        # do stuff
```

For more information, see these pages:

* [Events](plugins/events.md)
* [Event Names](reference/events-names.md)
{% endtab %}

{% tab title="Discord Objects" %}
```python
from bolt import Plugin
from bolt import command

class Example(Plugin):

    @command("kick me!")
    def on_kick(self, event):
        event.sender.kick(reason="You told me to!")
```

For more information, see these pages:

* [Discord Objects](advanced/bot-object.md)
{% endtab %}
{% endtabs %}

Bolt originally started out as a simple Trivia Bot that used long polling and webhooks to read and write to chat channels.

I became obsessed with making this bot more robust and at that time, no bots existed for Discord, so this bot evolved into a fully vetted framework that I could use to build functionality off of.

This project is a place I can experiment with design ideas and evolve a sense of personal code standards. I treat it more as an academic project to learn about new libraries and tools available to me as Python continues to grow.

