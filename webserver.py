# Script to demo a simple webserver

# Orig code is from
#   https://medium.com/@akhilsamvarghese1234/from-blink-to-setting-up-a-webserver-with-esp32-using-micropython-73f3f3c1aa49

# Need to run wifi.py first (on the ESP32)

import socket
import network

# Get the ESP32 IP Address
wlan = network.WLAN(network.STA_IF)

if wlan.isconnected():
    ip = wlan.ifconfig()[0]
    print(f"ESP32 Web Server Running at http://{ip}")
else:
    print("ESP32 is not connected to Wi-Fi. Run main.py first!")
    raise SystemExit

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((ip, 80))  # Bind to port 80 (HTTP)
server_socket.listen(5)  # Listen for connections

while True:
    conn, addr = server_socket.accept()
    print("Client connected from:", addr)
    
    request = conn.recv(1024)  # Read request from client
    print("Request:", request)

    # Create an HTML response
    response = """\
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head><title>ESP32 Web Server</title></head>
<body>
    <h1>Welcome to ESP32 Web Server!</h1>
    <p>Your ESP32 is running a simple web server.</p>
</body>
</html>
"""
    
    conn.send(response.encode())  # Send response
    conn.close()  # Close connection
