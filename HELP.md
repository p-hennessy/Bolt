# API

## Core
The core is what holds the bot together. It is a single place where all the features of the bot come together. Think of the core as the bot API. In Object Oriented Programming terms, the core composes the other instances to create it's functionality.

What does this mean for you? Plugins access the bot API by refering to `self.core`. Most plugins won't need to do anything fancy, but everything is available to you via the bot core.


## Bot Config
Config should be self explanatory.
If this is your first time running Arcbot; you need to rename `settings-example.py` to `settings.py`; otherwise the bot won't recognize it.

The config is where you tell the bot what it needs to know at start up.

Heres what you need to set:

- `trigger` - This will let Arcbot know you're refering to it. Commands by default must be prefixed with this trigger.
- `connector` - A string to denote which connector you want to use. You can find the names in the `connectors` folder.
- `connectorOptions` - Will depend on the connector, but this is anything important for the connector to work
- `plugins` - A list of plugins you want to load from startup. It is HIGHLY recommended to leave the ACL and Manage plugins there

## Writing a Plugin
To write a plugin; you need a few things to start.

```
from core.Plugin import Plugin
from core.Decorators import *

class Sample(Plugin):
    def activate(self):
        pass

```

Above is the bare minimum needed to have it considered a plugin.

Notice that it is a subclass to core.Plugin. This gives it some special properties and gives a few convenience methods.

## Creating a command
Commands are stupid simple to create.

You need 2 things:
- A regex used to determine when to run the code below
- The code to be run

Example:
```
    @command("^ping$")
    def ping(self, msg):
        self.say(msg.channel, "pong")

```

The `@command` decorator will naturally register the code under it as a command.
You supply a regex so that it knows when this code should be run.

## More advanced commands
Now that you know the basics, let's see what else we can do:

Example:
```
    @command("kappa", access=100, useDefaultTrigger=False)
    def kappa(self, msg):
        self.reply(msg, "You mean Kappa?")
```

The `@command` decorator can take more arguments.
- `access` is the amount (0-1000) that it takes to run that command. This is useful for when you want to restrict access to a command by certain users
- `useDefaultTrigger` tells the bot if this command needs to use the default trigger defined in the bot config. If not, it will run the code when that regex is matched.



## Built-in Plugin Methods and Decorators
`self.say`  - Takes a channelid and a string message as arguments. This will 'say' the string in that channel. You'll likely just be posting in the channel the message came from: `msg.channel`
`self.reply` - Takes a message and string as arguments. This will use the connectors version of mentioning to direct a response at the user.

`self.activate`
    This method is called immediately when the plugin is loaded. Any code you would want to put in an `init` function should go here. In OOP terms; this is the plugin's constructor

    Why not just use `__init__()`?
        The way that plugins have to be loaded by Python; this would not work correctly.

`self.deactivate`
    This method is called immediately when the plugin is unloaded. It is important to do any cleanup here (such as joining threads, closing file descriptors, etc)
    In OOP terms; this is the plugin's destructor
