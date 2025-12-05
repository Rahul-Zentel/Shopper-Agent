import os
from typing import Dict, Optional

import requests


SCRAPINGBEE_API_KEY = os.getenv("SCRAPINGBEE_API_KEY")
if SCRAPINGBEE_API_KEY:
    SCRAPINGBEE_API_KEY = SCRAPINGBEE_API_KEY.strip().strip("'").strip('"')


class ScrapingBeeError(Exception):
    """Raised when ScrapingBee returns an error response."""


def fetch_html_with_scrapingbee(
    url: str,
    params: Optional[Dict[str, str]] = None,
    render_js: bool = True,
    country_code: Optional[str] = None,
) -> str:
    """
    Fetch a rendered HTML page using ScrapingBee.

    Expects the API key in the SCRAPINGBEE_API_KEY environment variable.
    """
    if not SCRAPINGBEE_API_KEY:
        raise ScrapingBeeError(
            "SCRAPINGBEE_API_KEY environment variable is not set. "
            "Set it to your ScrapingBee API key before running the scraper."
        )

    base_params: Dict[str, str] = {
        "api_key": SCRAPINGBEE_API_KEY,
        "url": url,
    }

    # Enable JS rendering for modern ecommerce sites
    if render_js:
        base_params["render_js"] = "true"

    # Geo-targeting (e.g. US for walmart.com, amazon.com, etc.)
    if country_code:
        base_params["country_code"] = country_code

    if params:
        base_params.update(params)

    resp = requests.get("https://app.scrapingbee.com/api/v1/", params=base_params, timeout=60)
    if resp.status_code != 200:
        error_msg = f"ScrapingBee request failed: {resp.status_code} - {resp.text}"
        print(f"DEBUG: {error_msg}")
        raise ScrapingBeeError(error_msg)

    return resp.text




