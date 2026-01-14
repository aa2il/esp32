# Script to demo a simple interactive webserver

# Orig code is from
#   https://medium.com/@akhilsamvarghese1234/from-blink-to-setting-up-a-webserver-with-esp32-using-micropython-73f3f3c1aa49

# Need to run wifi.py first (on the ESP3

import machine
import socket
import network

LED_PIN=2    # 5                   # D2 is the On-board blue LED, D5 has an external LED attached to it

# Ensure Wi-Fi is connected
wlan = network.WLAN(network.STA_IF)
if not wlan.isconnected():
    print("Wi-Fi not connected. Please run your Wi-Fi connection script first!")
    raise SystemExit
ip = wlan.ifconfig()[0]
print("ESP32 Web Server Running at: http://" + ip)

# Set up LED (for an external LED wired as active-high)
led = machine.Pin(LED_PIN, machine.Pin.OUT)
led.value(0)  # Assuming active-high: 0 means LED off

# Create and bind socket to port 80
s = socket.socket()
addr = ('0.0.0.0', 80)

s.bind(addr)                      # Throws an error if we try to rerun

s.listen(5)
print("Listening on", addr)

def generate_page(message=""):
    html = """<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>ESP32 LED Control</title>
    <style>
      html, body {
         height: 100%%;
         margin: 0;
         padding: 0;
         display: flex;
         flex-direction: column;
         align-items: center;
         justify-content: center;
         background: #1e3c72; /* Solid background color */
         font-family: Arial, sans-serif;
         color: #ffffff;
      }
      h1 {
         font-size: 2.5em;
         margin-bottom: 20px;
      }
      p {
         font-size: 1.5em;
         margin-bottom: 20px;
      }
      .btn {
         background-color: #ff9800;
         border: none;
         color: white;
         padding: 20px 40px;
         font-size: 1.5em;
         margin: 10px;
         cursor: pointer;
         border-radius: 8px;
         transition: background-color 0.3s ease;
      }
      .btn:hover {
         background-color: #e68900;
      }
    </style>
  </head>
  <body>
    <h1>ESP32 LED Control</h1>
    <p>%s</p>
    <p>
      <a href="/on"><button class="btn">Turn LED ON</button></a>
      <a href="/off"><button class="btn">Turn LED OFF</button></a>
    </p>
  </body>
</html>""" % message
    return html

while True:
    conn, client_addr = s.accept()
    print("Client connected from", client_addr)
    request = conn.recv(1024).decode()
    print("Request:", request)
    
    message = ""
    # Process the request to update LED status
    if "GET /on" in request:
        led.value(1)  # Turn LED ON (active-high)
        message = "LED is ON"
    elif "GET /off" in request:
        led.value(0)  # Turn LED OFF (active-high)
        message = "LED is OFF"
    
    # Always serve the main page with the updated status message
    response_body = generate_page(message)
    response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + response_body
    conn.send(response.encode())
    conn.close()

