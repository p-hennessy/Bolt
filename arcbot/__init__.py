from .core import Bot
from .plugin import Plugin

from .utils import find_plugins

from .event import Events as events
from .colors import Colors as colors

# Plugin decorators
from .webhook import webhook
from .command import command
from .event import subscribe
