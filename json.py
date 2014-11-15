#!/usr/bin/python

import simplejson as json

fileStream = open("questions.json", "r")

questions = json.load(fileStream)

print len(questions['pokemon'])

fileStream.close()