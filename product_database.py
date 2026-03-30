"""Product Database"""

from dataclasses import dataclass
import logging
from pathlib import Path
import sqlite3

DB_DIR = Path('database')
DB_DIR.mkdir(exist_ok=True)
DB_FILE = DB_DIR / "products.db"

logger = logging.getLogger(__name__)


@dataclass
class ProductInfo:
    """Class for represing a Product in the ProductDatabase"""
    product_id: int
    url: str
    name: str
    price_when_added: float
    date_added: str
    lowest_price: float
    lowest_price_date: str


class ProductDatabase:
    """Class for handling the Product database"""

    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file

        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            name TEXT,
            price_when_added REAL,
            date_added TEXT,
            lowest_price REAL,
            lowest_price_date TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            price REAL,
            date_checked TEXT,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
        """)

        conn.commit()
        conn.close()


    def is_valid_product_id(self, product_id: int) -> bool:
        """Check if the product_id is in the product database"""
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()

        cur.execute("SELECT id FROM products WHERE id = ?", (product_id,))
        result = cur.fetchone()
        conn.close()

        if result:
            return True

        return False


    def add_product(self, url: str, name: str, date: str, price: float):
        """Add a product to the database"""
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()

        cur.execute("SELECT id FROM products WHERE url = ?", (url,))
        result = cur.fetchone()

        if result is None:
            logger.info("Adding product '%s' from '%s'", name, url)
            cur.execute("""
                INSERT INTO products (url, name, price_when_added, date_added, lowest_price, lowest_price_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (url, name, price, date, price, date))
            product_id = cur.lastrowid

            logger.info("Adding info to price_history")
            cur.execute("""
                INSERT INTO price_history (product_id, price, date_checked)
                VALUES (?, ?, ?)
            """, (product_id, price, date))
        else:
            logger.info("Product from '%s' already exists. Product id=%d", url, result[0])

        conn.commit()
        conn.close()


    def remove_product_by_id(self, product_id: int) -> None:
        """Delete product from prooducts and price_history table by using product id"""
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()

        cur.execute("SELECT id FROM products WHERE id = ?", (product_id,))
        result = cur.fetchone()

        if result is None:
            logger.info("Product id '%d' does not exist in database", product_id)
            conn.close()
            return

        logger.info("Removing product '%d' from products and price_history", product_id)
        cur.execute("""
            DELETE FROM products WHERE id = ?
        """, (product_id,))
        cur.execute("""
            DELETE FROM price_history WHERE product_id = ?
        """, (product_id,))

        conn.commit()
        conn.close()


    def remove_product_by_url(self, url: str) -> None:
        """Delete product from prooducts and price_history table by using product url"""
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()

        cur.execute("SELECT id FROM products WHERE url = ?", (url,))
        result = cur.fetchone()

        if result is None:
            logger.info("Product from '%s' does not exist in database", url)
            conn.close()
            return

        product_id = result[0]
        logger.info("Removing product from '%s' from products and price_history", url)
        cur.execute("""
            DELETE FROM products WHERE id = ?
        """, (product_id,))
        cur.execute("""
            DELETE FROM price_history WHERE product_id = ?
        """, (product_id,))

        conn.commit()
        conn.close()


    def update_lowest_price(self, product_id: int, price: float, date: str) -> None:
        """Update the lowest price data for a product"""
        logger.info("Updating lowest price data for product_id: %d", product_id)
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()

        cur.execute("""
            UPDATE products
            SET lowest_price = ?,
                lowest_price_date = ?
            WHERE id = ?
        """, (price, date, product_id))

        conn.commit()
        conn.close()


    def get_product_id_list(self) -> list[int]:
        """Return list of all product IDs"""
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()

        cur.execute("SELECT id FROM products")
        results = cur.fetchall()
        id_list = [row[0] for row in results]
        conn.close()

        id_list.sort()
        return id_list


    def get_product_from_id(self, product_id: int) -> ProductInfo | None:
        """Return ProductInfo object for a given product id"""
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()

        cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        result = cur.fetchone()
        conn.close()

        if result is None:
            return None

        return ProductInfo(*result)


    def get_last_product_price_from_id(self, product_id: int) -> tuple[int, str] | None:
        """Return last (price, date_checked) for a given product_id"""
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()

        cur.execute("""
            SELECT price, date_checked
            FROM price_history
            WHERE product_id = ?
            ORDER BY date_checked DESC
            LIMIT 1
        """, (product_id,))
        result = cur.fetchone()
        conn.close()

        return result


    def add_price_history(self, product_id: int, price: float, date: str) -> None:
        """Add new entry for product price history"""
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()

        if self.is_valid_product_id(product_id):
            logger.info("Adding info to price_history")
            cur.execute("""
                INSERT INTO price_history (product_id, price, date_checked)
                VALUES (?, ?, ?)
            """, (product_id, price, date))
        else:
            logger.warning("Invalid product ID. Cann not add info to price_history")

        conn.commit()
        conn.close()
