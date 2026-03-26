# Amazon Price Watch

`amazon-price-watch` is a small Python CLI for tracking Amazon product prices, storing price history in SQLite, and optionally sending email alerts when a product drops below the price it had when you added it.

## Features

- Add an Amazon product to the local watch list from a product URL
- Store tracked products and price history in a SQLite database
- Update the latest price for every tracked product
- List tracked products, including current and lowest observed prices
- Send an HTML email alert for products now cheaper than their original tracked price
- Write logs to both the console and `logs/app.log`

## Requirements

- Python 3.14 or compatible Python 3.x environment
- Internet access to fetch Amazon product pages
- SMTP credentials if you want to send email alerts

## Installation

1. Create and activate a virtual environment.
2. Install dependencies from `requirements.txt`.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuration

Email alerts are configured through a `.env` file in the project root.

Example:

```env
APP_EMAIL_NAME="Amazon Price Watch"
APP_EMAIL_ADDR="your-email@example.com"
EMAIL_PASS="your-app-password"
EMAIL_SMTP_SERVER="smtp.example.com"
EMAIL_SMTP_PORT=587
```

Notes:

- Use an app password or equivalent SMTP credential, not your normal mailbox password.
- The `.env` file is ignored by git.
- Email settings are only needed when using `--send`.

## Usage

Run the main script with one of the supported options:

```powershell
python amazon_price_watch.py --help
```

### Add a product

```powershell
python amazon_price_watch.py --add "https://www.amazon.com/dp/ASIN"
```

This fetches the product title and current price from Amazon, then stores:

- product URL
- product name
- price when added
- date added
- initial lowest price
- initial price history entry

### Remove a product

```powershell
python amazon_price_watch.py --remove "https://www.amazon.com/dp/ASIN"
```

This removes the product from both the `products` and `price_history` tables.

### List tracked products

```powershell
python amazon_price_watch.py --list
```

The output includes:

- product ID
- name
- URL
- price when added
- date added
- last recorded price
- date of the last recorded price
- lowest recorded price
- date of the lowest recorded price

### Update all prices

```powershell
python amazon_price_watch.py --update
```

This fetches the current price for each tracked product and appends a new record to `price_history`. If the new price is the lowest seen so far, the `products` table is updated as well.

### Update prices and send alerts

```powershell
python amazon_price_watch.py --update --send
```

After updating prices, the script emails a summary of any products whose latest price is lower than the price recorded when they were first added.

## Database and Logs

The project creates these directories automatically:

- `database/` for the SQLite database at `database/products.db`
- `logs/` for the rotating log file at `logs/app.log`

Both directories are ignored by git.

## Project Structure

```text
amazon_price_watch.py   Main CLI entry point
amazon.py               Amazon scraping helpers
product_database.py     SQLite database layer
send_email.py           Email generation and delivery
logging_config.py       Console and rotating file logging
templates/              HTML email templates
database/               Generated SQLite database
logs/                   Generated log files
```

## Limitations

- Amazon page markup can change, which may break product name or price parsing.
- Some Amazon pages may block requests or return content that does not include the expected price fields.
- Alerts are triggered only when the latest price is lower than the original added price, not when the price merely drops relative to the previous check.
