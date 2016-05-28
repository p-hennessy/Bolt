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
import logging

class Watchdog():
    def __init__(self, core):
        self.logger = logging.getLogger(__name__)
        self.core = core

        # Reconnection settings
        self.connection_retry = self.core.config.connection_retry
        self.connection_timeout = self.core.config.connection_timeout
        self.connection_died = time.time()

    def start(self):
        while True:
            time.sleep(1)

            # Check if connector is connected
            if self.core.connection.connected == False and time.time() - self.connection_died >= self.connection_timeout:
                self.core.connection.disconnect()
                self.logger.warning("Connection is closed, attempting reconnection.")

                for connectionAttempt in range(0, self.connection_retry):
                    self.core.login()

                    if(self.core.connection.connected):
                        break

                    time.sleep(1)

                if not self.core.connection.connected:
                    self.connection_died = time.time()
                    self.logger.warning("Reconnection failed. Will retry in {} seconds.".format(self.connection_timeout))
