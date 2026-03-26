"""Amazon helper functions"""

from dataclasses import dataclass
import logging
from bs4 import BeautifulSoup
import requests


CUSTOM_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}


logger = logging.getLogger(__name__)


@dataclass
class AmazonProduct:
    """Class for representing an Amazon product"""
    name: str
    url: str
    price: float


def get_amazon_product_from_url(url: str) -> AmazonProduct | None:
    """Look up an Amazon product from the URL and return an AmazonProduct"""
    with requests.Session() as s:
        product_page = s.get(url, headers=CUSTOM_HEADERS, timeout=5)
        if product_page.status_code != 200:
            logger.error("Error requesting URL: '%s'. Response = %d", url, product_page.status_code)
            return None

        soup = BeautifulSoup(product_page.text, "html.parser")

        product_name = soup.find("span", attrs={"id": "productTitle"})
        if not product_name:
            logger.error("Could not find product name on page '%s'", url)
            return None

        price_whole = soup.find("span", class_="a-price-whole")
        if not price_whole:
            logger.error("Could not find price_whole on page '%s'", url)
            return None

        price_fraction = soup.find("span", class_="a-price-fraction")
        if not price_fraction:
            logger.error("Could not find price_fraction on page '%s'", url)
            return None

        product_name_text = product_name.get_text(separator=" ", strip=True)
        price_whole_text = price_whole.get_text(separator=" ", strip=True).replace(".", "").strip()
        price_fraction_text = price_fraction.get_text(separator=" ", strip=True)
        price: float = float(price_whole_text) + float(price_fraction_text)/100

    return AmazonProduct(product_name_text, url, price)
