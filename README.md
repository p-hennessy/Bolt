# About CL4M-B0T
An extensible chatbot written entirely in Python. 
This bot was designed to be easy to extend and maintain. It follows very stict code and documentation standards.

CL4M-B0T is open source software and released under the GPL v3 license.

# Installing / Running
Everything about CL4M-B0T is self contained.

Running it is as simple as downloading this repo; and running the entry point `bot.py` with Python 2.7

Configuration for the bot itself can be found in `conf/settings.py`

# Features

### Connectors
Currently, CL4M-B0T only supports the unoffical Discord connector. A full API has yet to be released for Discord, this connector is based on reverse engineering.

I have plans to fully support Slack, which is not all that different than Discord

### Plugin System
Using the power of Python, CL4M-B0T gets all of it's functionality from plugins. The plugin system takes care of all the annoying code behind the scenes, so the code in a plugin in minimal.

Plugins have access to anything in the bot; so a plugin *can* do anything; but the exposed API is simple and limited, but will serve most needs

# Credits
Credit must be given to the developers behind Hubot and Errbot projects; a lot of this bot was inspired by those projects.
