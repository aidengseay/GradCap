################################################################################
# LED GRAD CAP
# Created by Aiden Seay | Fall 2026
################################################################################
# IMPORTS
import network
import socket
import time

################################################################################
# CONSTANTS

SSID = "GradCapMatrix"
PASSWORD = "Gr@d$WIN2026!@"

################################################################################

# define access point
ap = network.WLAN(network.AP_IF)

ap.active(False)

# set access point configurations
ap.config(
    essid=SSID,
    password=PASSWORD,
    authmode=network.AUTH_WPA2_PSK
)
ap.active(True)

# wait until access point is active
while not ap.active():
    time.sleep(0.1)

# display information for debugging
print(f"{SSID} Wi-Fi started")
print("SSID:", SSID)
print("IP address:", ap.ifconfig()[0])
print("Auth mode:", ap.config("authmode"))

# set server socket
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", 80))
server.listen(1)

while True:

    client, address = server.accept()
    
    print("Client connected from:", address)

    request = client.recv(1024)

    print("Request:")
    print(request)

    client.send(
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/plain\r\n"
        "Connection: close\r\n"
        "\r\n"
        "Hello from the Matrix!"
    )

    client.close()
