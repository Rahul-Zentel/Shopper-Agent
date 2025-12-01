import urllib.request
import json
from typing import Optional


def get_public_ip(timeout: int = 3) -> Optional[str]:
    """
    Fetches the public IP of the server (or local machine).

    This is an additive utility and does not affect existing features.
    """
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=json", timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("ip")
    except Exception:
        # Silent failure with graceful fallback handled by callers.
        return None


def get_region_from_ip(ip_address: Optional[str] = None, timeout: int = 3) -> str:
    """
    Determines the region (Country) from an IP address.

    - If ip_address is None or clearly localhost, it tries to fetch the public IP.
    - On any failure, it **always** falls back to \"India\" to avoid impacting flows.
    """
    # Handle localhost/private IPs by fetching public IP
    if not ip_address or ip_address in ("127.0.0.1", "::1", "localhost"):
        ip_address = get_public_ip(timeout=timeout)

    if not ip_address:
        # Fallback region to keep behaviour deterministic and non-breaking
        return "India"

    try:
        # Using a free geolocation API. In production, prefer a paid service or local DB.
        url = f"http://ip-api.com/json/{ip_address}"
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
            if data.get("status") == "success":
                country = data.get("country", "")
                return country or "India"
    except Exception:
        # Any error should not break flows; just fall back to India
        pass

    return "India"


