################################################################################
# WIFI SUPPORTING FUNCTIONS
# Created by Aiden Seay | Fall 2026
################################################################################
# IMPORTS

from config import SSID, PASSWORD
import network
import time

################################################################################

def start_access_point():

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

    return ap

################################################################################