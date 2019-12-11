# Command Hooks

## Overview

{% hint style="warning" %}
Be careful when hooking commands, it may slow down the bot if this handler is expensive.
{% endhint %}

Command hooks are a way to provide a middleware. It'll fire this handler before it will run the intended handler.

You can use this for:

* Verifying the user is allowed to run this command
* Create a filter for which events can invoke a certain command

## Examples

{% tabs %}
{% tab title="User Access" %}
```python
from bolt import pre_command_hook

@pre_command_hook()
def check_access(self, command, event):
    author = self.bot.users.find_one({"id": event.author.id})
    access_level = author.get("access_level")

    if not access_level >= command.access_level:
        event.channel.say("You don't have access to that command.")
        return False
    else:
        return True
```
{% endtab %}
{% endtabs %}

