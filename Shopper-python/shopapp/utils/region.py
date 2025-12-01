import urllib.request
import json
import socket

def get_public_ip():
    """
    Fetches the public IP of the server (or local machine).
    """
    try:
        with urllib.request.urlopen('https://api.ipify.org?format=json', timeout=3) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('ip')
    except Exception as e:
        print(f"Error fetching public IP: {e}")
        return None

def get_region_from_ip(ip_address: str = None) -> str:
    """
    Determines the region (Country) from an IP address.
    If ip_address is None or private (localhost), it tries to fetch the public IP.
    Defaults to 'India' if detection fails.
    """
    # Handle localhost/private IPs by fetching public IP
    if not ip_address or ip_address in ("127.0.0.1", "::1", "localhost"):
        ip_address = get_public_ip()
    
    if not ip_address:
        print("Could not determine IP, defaulting to India")
        return "India"

    try:
        # Use a free geolocation API (e.g., ip-api.com)
        # Note: In production, use a paid service or local DB like GeoIP2
        url = f"http://ip-api.com/json/{ip_address}"
        with urllib.request.urlopen(url, timeout=3) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('status') == 'success':
                country = data.get('country', '')
                print(f"Detected Country: {country} for IP: {ip_address}")
                return country
    except Exception as e:
        print(f"Error resolving region for IP {ip_address}: {e}")
    
    return "India"  # Default fallback
