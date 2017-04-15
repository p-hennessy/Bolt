"""
    Class Name : Watchdog

    Description:
        Main thread ends up here; where it will monitor various status' of the bot and act accordingly

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import time
import sys
import logging

class Watchdog():
    def __init__(self, core):
        self.logger = logging.getLogger(__name__)
        self.core = core

        # Reconnection settings
        self.connection_retry = self.core.connection_retry
        self.connection_timeout = self.core.connection_timeout

    def start(self):
        while True:
            time.sleep(1)

            if not self.core.connection.connected:
                self.logger.warning("Connection is closed, attempting reconnection")

                for retry in range(0, self.connection_retry):
                    if self.core.connection.connected:
                        break

                    try:
                        self.core.disconnect()
                        self.core.connect()
                    except:
                        time.sleep(10)
                        continue

                else:
                    self.logger.warning("Failed to reconnect after {} tries. Sleeping for {} seconds.".format(self.connection_retry, self.connection_timeout))
                    time.sleep(self.connection_timeout)
