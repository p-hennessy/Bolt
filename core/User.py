"""
    Class Name : User

    Description:
        Provides staging area for user data

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from peewee import *

class User(Model):
    id       = IntegerField(primary_key=True)
    username = CharField(max_length=25, default='None')
    access   = IntegerField()

    
