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
        self.connectionRetry = self.core.config.connectionRetry
        self.connectionTimeout = self.core.config.connectionTimeout
        self.connectionDied = 0

    def start(self):
        while True:
            time.sleep(1)

            # Check if connector is connected
            if(self.core.connection.connected == False and time.time() - self.connectionDied >= self.connectionTimeout):
                self.core.connection.disconnect()
                self.logger.warning("Connection is closed, attempting reconnection.")

                for connectionAttempt in range(0, self.connectionRetry):
                    self.core.login()

                    if(self.core.connection.connected):
                        break

                if not self.core.connection.connected:
                    self.connectionDied = time.time()
                    self.logger.warning("Reconnection failed. Will retry in {} seconds.".format(self.connectionTimeout))
