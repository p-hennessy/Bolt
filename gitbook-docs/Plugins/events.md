# Events

## Overview

Bolt can invoke a handler for any [websocket event](https://discordapp.com/developers/docs/topics/gateway#commands-and-events-gateway-events) from Discord.

## Example

```python
from bolt import subscriber
from bolt.discord import Events

@subscriber(Events.GUILD_MEMBER_UPDATE)
def on_guild_member_update(self, event):
    # handle stuff
```

## Reference

{% page-ref page="../reference/events-names.md" %}



