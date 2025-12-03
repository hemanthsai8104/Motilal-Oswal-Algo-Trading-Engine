# utils.py
import requests
import uuid

def get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=3).text.strip()
    except:
        return "127.0.0.1"

def get_mac_address():
    try:
        mac = uuid.getnode()
        return ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
    except:
        return "00:00:00:00:00:00"