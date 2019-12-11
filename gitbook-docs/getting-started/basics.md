# Basics

## Overview

Bolt derives all functionality from plugins.

Bolt provides a super-class for plugins to use which handles the boilerplate. We want to get out of the way and allow plugin authors to get down to business of just writing the code they need.

## Example

```python
from bolt import Plugin
from bolt import command

class Example(Plugin):

    @command("hello")
    def ping(self, message):
        self.say(message.channel_id, "world!")
```

## Plugin Loading & Unloading

Plugins will automatically call a method named `activate` and `deactivate`when they are loaded and unloaded respectively. Think of this like the `__init__` function.

You can enable / disable, load or unload a plugin if you desire. This can be very useful for testing your plugins. The plugin superclass has all of the methods listed above exposed for this purpose. You can access the plugins list on the bot object: `self.bot.plugins`

The reason we don't expose init itself is that we need to load the object instance, and need to be sure it runs things from the super-init function so we can uniformly expose a clean API to plugin authors.

Plugins are loaded dynamically, and are namespaced from one another. It should not be possible to load the same plugin twice, or overwrite another plugin.

