################################################################################

# A simple web client for the Yeti GoalZero Battery

# Use Thonny to upload code to ESP32 - Interpreter is for ESP32 VROOM varient

# Need to upload credentials.py to ESP32 first.  Easiest way ia to enable View->Files
# and then right-click on This Computer->....->credentials.py -> Uploead To -> ...

################################################################################

import network
import urequests2 as urequests
import time
from credentials2 import *

################################################################################

URL='http://10.1.1.1'
HEADER = {
    "Content-Type": "application/json",
    "User-Agent": "YetiApp/1340 CFNetwork/1125.2 Darwin/19.4.0",
    "Connection": "keep-alive",
    "Accept": "application/json",
    "Accept-Language": "en-us",
    "Accept-Encoding": "gzip, deflate",
    "Cache-Control": "no-cache",
}
 
################################################################################

# Function to connect to Yeti Wi-Fi network
def connect_to_wifi(SSID,PASSWORD):

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    print("Connecting to Wi-Fi...")
    while not wlan.isconnected():
        print('...waiting...')
        time.sleep(0.5)
    print("Connected! Network configuration:", wlan.ifconfig())
    
    return wlan

def EOR():
    print('<EOR>')

def send_get_request(URL,VERBOSITY=0):
    try:

        data={}
        if VERBOSITY>0:
            print(f"Sending GET request to {URL}")
        response = urequests.get(URL,timeout=5)

        #print('state=',json.dumps(self.state,indent=4))
        #print('Status=',resp.status_code)
        
        # Process the response payload
        if response.status_code == 200:
            if VERBOSITY>0:
                print("Success!")
            data = response.json()
            print('data=',data)
        else:
            print("Failed. Status Code:", response.status_code)
        
        # Always close your network connection socket
        response.close()

    except Exception as e:
        print("An error occurred:", e)

    return data


def set_state(URL,key,onoff):
    print('\n=========== SET STATE ==============\n')

    post={}
    payload = { key : onoff }
    try:
        resp = urequests.post(URL+'/state',headers=HEADER,json=payload)
        post = resp.json()
        print('Status=',resp.status_code)
        print('post=',post)

    except Exception as e:
        print("YETI CLIENT - SET STATE: An error occurred:", e)
    
    return post


################################################################################
            
# Here we go ... finally!
wlan=connect_to_wifi(SSID,PASSWORD)

# Infinite loop to service requests from data aggregator
while True:
    cmd0=input("? ")
    cmd=cmd0.upper()

    if cmd=='ID':
        print('Yeti Web Client v0.1')
        EOR()

    elif cmd=='NET':
        if wlan.isconnected():
            print("Network configuration:", wlan.ifconfig())
        else:
            print('No network connection :-(')
        EOR()

    elif cmd=='RECONNECT':
        wlan=connect_to_wifi(SSID,PASSWORD)
        EOR()

    elif cmd=='SYSINFO':
        data=send_get_request(URL+"/sysinfo")
        EOR()
        
    elif cmd=='STATE':
        data=send_get_request(URL+"/state")
        EOR()
        
    elif cmd[0:4]=='SET ':
        a=cmd0.split(' ')
        key=a[1]
        status=a[2]
        set_state(URL,key,status)
        EOR()
    
    else:
        print('Unrecognized cmd=',cmd)
        EOR()

    
