"""
    Class Name : ConfigParser

    Description:

    Contributors:
        - Patrick Hennessy

    License:
        PhilBot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import json

def getConfig(fileName):
    configData = None

    with open(fileName) as file:
        configData = json.load(file)
    
    return configData
