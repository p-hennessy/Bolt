#1/usr/bin/python

import requests

url = "https://patacave.slack.com/services/hooks/incoming-webhook?token=PiGeLJIXj00PbaUdSVbVfgDy"

payload = '{"channel": "#general", "username": "Trebek 1.0", "text": "The matrix has you..."}'

print requests.post(url, data=payload)