# Script to connection to local wifi

# Orig code is from
#   https://medium.com/@akhilsamvarghese1234/from-blink-to-setting-up-a-webserver-with-esp32-using-micropython-73f3f3c1aa49

# Need to upload credentials.py to ESP32 first.  Easiest way ia to enable View->Files
# and then right-click on This Computer->....->credentials.py -> Uploead To -> ...

import network
import time
from credentials import *

# Initialize Wi-Fi in station mode
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Check if Wi-Fi is enabled
if not wlan.active():
    print("Failed to activate Wi-Fi!")
    raise SystemExit

# Connect to Wi-Fi network
wlan.connect(SSID,PASSWORD)

# Wait for connection
for _ in range(10):  # Try for 10 seconds
    if wlan.isconnected():
        break
    time.sleep(1)

# Check final status
if wlan.isconnected():
    print('Connected, IP address:', wlan.ifconfig()[0])
else:
    print("Failed to connect to Wi-Fi. Check SSID & Password!")
