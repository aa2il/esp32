# Script to demonstrate a simple web client

# Orig code is from Google AI slop.
# And of course, it DID NOT WORK - world timeapi.org no longer exists!

# Use Thonny to upload code to ESP32 - Interpreter is for ESP32 VROOM varient

# Need to upload credentials.py to ESP32 first.  Easiest way ia to enable View->Files
# and then right-click on This Computer->....->credentials.py -> Uploead To -> ...

import network
import urequests
import time
from credentials import *

# 1. Connect to local Wi-Fi network
#SSID = "YOUR_WIFI_SSID"
#PASSWORD = "YOUR_WIFI_PASSWORD"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Connecting to Wi-Fi...")
while not wlan.isconnected():
    time.sleep(0.5)

print("Connected! Network configuration:", wlan.ifconfig())


# 2. Define the Target URL (Example: Public API)
#URL = "http://worldtimeapi.org"
URL = "https://time.now/developer/api/timezone/UTC"

try:
    print(f"Sending GET request to {URL}...")
    
    # 3. Execute the HTTP GET request
    response = urequests.get(URL)
    
    # 4. Process the response payload
    if response.status_code == 200:
        print("Success!")
        data = response.json() # Parse JSON data automatically
        print("Current UTC Datetime:", data["datetime"])
    else:
        print("Failed. Status Code:", response.status_code)
        
    # 5. Always close your network connection socket
    response.close()

except Exception as e:
    print("An error occurred:", e)
    


    

