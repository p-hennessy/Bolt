#1/usr/bin/python

import requests

url = "https://patacave.slack.com/services/hooks/incoming-webhook?token=PiGeLJIXj00PbaUdSVbVfgDy"

payload = '{"channel": "#general", "username": "webhookbot", "text": "This is posted to #general and comes from a bot named webhookbot.", "icon_emoji": ":ghost:"}'

r = requests.post(url, data=payload)

print r
