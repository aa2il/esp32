# Script to demonstrate a simple web client

# Orig code is from Duck-Duck-Go AI slop.
# Use Thonny to upload code to ESP32 - Interpreter is for ESP32 VROOM varient

# Need to upload credentials.py to ESP32 first.  Easiest way ia to enable View->Files
# and then right-click on This Computer->....->credentials.py -> Uploead To -> ...

import network
import urequests
from credentials import *

# Connect to Wi-Fi
#ssid = 'your_SSID'
#password = 'your_PASSWORD'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    pass

print('Connected to Wi-Fi:', wlan.ifconfig())

# Send a GET request
response = urequests.get('http://example.com/api/data')
print('Response:', response.text)
response.close()

