##############################################################################
#
# Bare bones udp server to show how to connect to WiFi LAN and received/send
# some simple commands.  We also explore the real-time clock.
#
##############################################################################

import time
import socket
import network
from machine import Pin,RTC
from credentials import *
import ntptime
import select

##############################################################################

# User params
PORT=1234

##############################################################################

# Function to connect to wlan in STATION mode
# Probably should add a counter to avoid infinite loop
def wlan_connect(SSID,PASSWORD):
    print('WLAN CONNECT: SSID:',SSID,'\tPASSWD=',PASSWORD,'\tPORT=',PORT)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    #wlan.disconnect()
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(SSID,PASSWORD)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    
    return wlan

##############################################################################

# Init
s=None
led = Pin(2,Pin.OUT)
led.value(0)

# Connect to wifi
wlan=wlan_connect(SSID,PASSWORD)
con=wlan.isconnected()
print('Connected:',con)

# Play with Real-time clock
rtc = RTC()
#rtc.datetime((2017, 8, 23, 1, 12, 48, 0, 0)) # set a specific date and time
print('\nThe time at the tone is',rtc.datetime(),'\n')

print("Local time before synchronization：%s" %str(time.localtime()))
ntptime.settime()
print("Local time after synchronization：%s" %str(time.localtime()))
print('\nThe time at the tone is',rtc.datetime(),'\n')

if con:
  ip=wlan.ifconfig()[0]
  while(ip=='0.0.0.0'):
    time.sleep(1)
    ip=wlan.ifconfig()[0]
  print('ip=',ip)

  IP=wlan.ifconfig()
  print('IP:',wlan.ifconfig())
  #s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)  
  s.bind((ip,PORT))
  
  print('\nFrom the command line, issue the following command to turn the led on and off:')
  print('\necho -n 1 | nc -4u -w 1',ip,PORT)
  
  print('\nWaiting...')

  # Need an approach similar to lib/tcp_server.py
  if True:
      s.listen(4)
      while True:
        try:
          conn,addr=s.accept()
        except:
            pass
        else:
            print('New connection from',conn,addr)
            text = conn.recv(1024).decode("utf-8")
            print('text=',text)

        time.sleep(1)            
  
  # Very basic approach that doesn't work with hamlib
  while False:
    data,addr=s.recvfrom(1024)
    #data=s.recv(1024)
    print('Received:',data,'from',addr)
    #s.sendto(data+"***",addr) # Echo to client side of udp, adding ‘***’
    if int(data)==1:
      led.value(1)        #Turn on LED light
    else:
      led.value(0)        #Turn off the LED light.
        
else:
  print('Unable to connecct to WiFi Network')
    
  if (s):
    s.close()
  wlan.disconnect()
  wlan.active(False)


