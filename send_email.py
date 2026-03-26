"""Functions for generating and sending email"""

from email.message import EmailMessage
from email.utils import formataddr
import logging
import os
import smtplib
import ssl
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from jinja2 import Template
from product_database import ProductDatabase


HTML_EMAIL_TEMPLATE = "templates/email_template.html"
HTML_PRODUCT_ROWS_TEAMPLATE = "templates/product_rows.html"


logger = logging.getLogger(__name__)


def build_email(product_id_list: list[int]) -> str:
    """Build the email"""
    db = ProductDatabase()

    with open(HTML_PRODUCT_ROWS_TEAMPLATE, "r", encoding="utf-8") as file:
        product_row_template: Template = Template(file.read())

    products_html = ""
    for product_id in product_id_list:
        product_info = db.get_product_from_id(product_id)
        last_price_info = db.get_last_product_price_from_id(product_id)

        products_html += product_row_template.render(
            {
                "name": product_info.name,
                "old_price": f"{product_info.price_when_added:.2f}",
                "new_price": f"{last_price_info[0]:.2f}",
                "url": product_info.url
            }
        )

    with open(HTML_EMAIL_TEMPLATE, "r", encoding="utf-8") as file:
        email_template_html: Template = Template(file.read())

    email_html = email_template_html.render(
        {
            "ROWS": products_html
        }
    )

    return email_html


def send_price_alert_email(product_id_list: list[int]) -> str:
    """Send an email with new price information"""
    logger.info("Generating and sending alert email.")

    load_dotenv()
    sender_email_name = os.getenv("APP_EMAIL_NAME")
    sender_email_addr = os.getenv("APP_EMAIL_ADDR")
    app_email_pass = os.getenv("EMAIL_PASS")
    smtp_server = os.getenv("EMAIL_SMTP_SERVER")
    smtp_port = int(os.getenv("EMAIL_SMTP_PORT"))

    msg = EmailMessage()
    msg["Subject"] = "Amazon Price Watch Alert"
    msg["From"] = formataddr((sender_email_name, sender_email_addr))
    msg["To"] = sender_email_addr

    html_content = build_email(product_id_list)
    soup = BeautifulSoup(html_content, "html.parser")
    plain_text_content = soup.get_text()

    msg.set_content(plain_text_content)
    msg.add_alternative(html_content, subtype='html')

    return_message = ''
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(sender_email_addr, app_email_pass)
            server.send_message(msg)
        return_message = 'Email sent successfully'
    except smtplib.SMTPException as e:
        return_message = f'Error: {e}'

    return return_message
