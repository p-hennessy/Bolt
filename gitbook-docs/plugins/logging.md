# Logging

## Overview

Bolt uses the [Python logging library](https://docs.python.org/3/library/logging.html), so this should feel very familiar to Python developers.

The Bot will automatically create a logger for you to use and does the following:

* Logs to standard out in a human readable format
* Pretty colors!
* Logs to a file in JSON format, most log parsers can read this format
* Automatic log rotation

## Example

```python
from bolt import Plugin

def Example(Plugin):
    def activate(self):
        self.logger.debug("Debug")
        self.logger.info("Info")
        self.logger.warning("Warning")
        self.logger.error("Error")
        self.logger.critical("Critical")
```

