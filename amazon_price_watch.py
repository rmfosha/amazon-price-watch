"""Script for checking Amazon products"""

import argparse
from datetime import datetime
import logging
from amazon import get_amazon_product_from_url
from logging_config import setup_logging
from product_database import ProductDatabase
from send_email import send_price_alert_email


setup_logging(logging.INFO)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse script arguments"""
    parser = argparse.ArgumentParser(description="Amazon Price Watch")

    parser.add_argument(
        "--add",
        type=str.lower,
        help="URL for Amazon product to add"
    )

    parser.add_argument(
        "--remove",
        type=int,
        help="ID for Amazon product to remove"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all products in database"
    )

    parser.add_argument(
        "--update",
        action="store_true",
        help="Update all product prices in database"
    )

    parser.add_argument(
        "--send",
        action="store_true",
        help="Send email alert if any lower prices"
    )

    return parser.parse_args()


def print_products() -> None:
    """Print all the products"""
    db = ProductDatabase()

    id_list = db.get_product_id_list()
    print()
    for product_id in id_list:
        product_info = db.get_product_from_id(product_id)
        last_price_info = db.get_last_product_price_from_id(product_id)
        print(f"ID: {product_info.product_id}")
        print(f"Name: {product_info.name}")
        print(f"URL: {product_info.url}")
        print(f"Price when added: {product_info.price_when_added}")
        print(f"Date added: {product_info.date_added}")
        print(f"Last price: {last_price_info[0]}")
        print(f"Last price date: {last_price_info[1]}")
        print(f"Lowest price: {product_info.lowest_price}")
        print(f"Lowest price date: {product_info.lowest_price_date}\n")


def update_all_prices() -> None:
    """Check and update prices for all products"""
    db = ProductDatabase()

    id_list = db.get_product_id_list()
    for product_id in id_list:
        product_info = db.get_product_from_id(product_id)
        amazon_product = get_amazon_product_from_url(product_info.url)
        if amazon_product:
            now = datetime.now().isoformat()
            db.add_price_history(product_id, amazon_product.price, now)

            if amazon_product.price < product_info.lowest_price:
                db.update_lowest_price(product_id, amazon_product.price, now)


def get_lower_price_lisst() -> list[int]:
    """Return a list of product_id with latest price lower than price when added"""
    db = ProductDatabase()

    product_list: list[int] = []

    id_list = db.get_product_id_list()
    for product_id in id_list:
        product_info = db.get_product_from_id(product_id)
        last_price_info = db.get_last_product_price_from_id(product_id)
        if last_price_info[0] < product_info.price_when_added:
            product_list.append(product_id)

    return product_list


def main() -> None:
    """Main function"""
    logger.info("Amazon Price Watch starting")

    args = parse_args()
    if args.add:
        db = ProductDatabase()
        amazon_product = get_amazon_product_from_url(args.add)
        now = datetime.now().isoformat()
        db.add_product(amazon_product.url, amazon_product.name, now, amazon_product.price)
    elif args.remove:
        db = ProductDatabase()
        db.remove_product_by_id(args.remove)
    elif args.list:
        print_products()
    elif args.update:
        update_all_prices()
        if args.send:
            lower_price_product_id_list = get_lower_price_lisst()
            if lower_price_product_id_list:
                email_sent_status_msg = send_price_alert_email(lower_price_product_id_list)
                logger.info(email_sent_status_msg)
    else:
        print("No option selected. Use --help for detials.")

    return


if __name__ == "__main__":
    main()
