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

import sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
import threading

class Database():
    def __init__(self):
        self.connection = SqliteDatabase('bot.db')
        self.connection.connect()

    def __del__(self):
        self.connection.close()

    def addTable(self, tableClass):
        setattr(tableClass._meta, 'database', self.connection)
        setattr(self, tableClass.__name__, tableClass)

        self.connection.create_table(tableClass, safe=True)
