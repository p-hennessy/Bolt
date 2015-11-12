"""
    Class Name : Database

    Description:

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from peewee import *
from playhouse.kv import JSONKeyStore

import threading

class Database():
    def __init__(self, databaseName="databases/bot.db"):
        self.connection = SqliteDatabase(databaseName)
        self.connection.connect()
        self.lock = threading.Lock()
        self.keyStore = JSONKeyStore(database=self.connection)

    def __del__(self):
        try:
            self.connection.close()
        except:
            pass

    def addTable(self, tableClass):
        setattr(tableClass._meta, 'database', self.connection)
        setattr(self, tableClass.__name__, tableClass)

        self.connection.create_table(tableClass, safe=True)
