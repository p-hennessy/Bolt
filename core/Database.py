"""
    Class Name : Database

    Description:

    Contributors:
        - Patrick Hennessy

    License:
        CL4M-B0T is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import shelve
import os.path

class Database():
    def __init__(self, name):
        self.fileName = "databases/" + name + ".db"
    
    def get(self, key):
        shelf = shelve.open(self.fileName)
        value = shelf[key]

        shelf.close()
        return value

    def set(self, key, value):
        shelf = shelve.open(self.fileName)
        shelf[key] = value

        shelf.close()
