import time
import os
import logging
import asyncio
import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram import Bot

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Load Telegram bot credentials
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN", "")  # Replace with GitHub Secrets or .env
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")  # Replace with your chat ID

# Initialize the Telegram bot
bot = Bot(token=API_TOKEN)

# Load accounts from environment variables
def load_accounts():
    accounts = []
    for i in range(1, 24):  # Modify range for more accounts
        account = {
            "email": os.getenv(f"EMAIL{i}"),
            "password": os.getenv(f"PASSWORD{i}"),
            "server_name": os.getenv(f"SERVER_NAME{i}")
        }
        if all(account.values()):  # Ensure all fields are populated
            accounts.append(account)
    return accounts

# Async function to send a Telegram message
async def send_telegram_message(message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
        logger.info("Message sent to Telegram.")
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

# Function to extract item information
def item_information(driver, account_email, server_name):
    try:
        login_count_text = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/section/div/div/div[2]/h5"))
        ).text
        login_days = int(login_count_text.split(":")[1].split()[0])

        claimed_day_selector = f"#xexchange > div:nth-child({login_days}) > div.reward-point"
        claimed_item_selector = f"#xexchange > div:nth-child({login_days}) > div.reward-name"

        claimed_day = driver.find_element(By.CSS_SELECTOR, claimed_day_selector).text
        claimed_item = driver.find_element(By.CSS_SELECTOR, claimed_item_selector).text

        result_message = f"""
        *CLAIM DETAILS*

━━━━━━━━━━━━━━━━━━━━━━━━

➤ *Claimed   :* {claimed_day}
➤ *Item      :* {claimed_item}

━━━━━━━━━━━━━━━━━━━━━━━━

*Server     :* {server_name}
*Email      :* {account_email}
"""

        asyncio.run(send_telegram_message(result_message))

    except Exception as e:
        logger.error(f"Error extracting item information: {e}")

# Function to claim item for a specific account
def claim_item_for_account(account):
    try:
        logger.info(f"Starting automation for account: {account['email']}")

        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        # Path to chromedriver
        driver_path = os.getenv("CHROMEDRIVER_PATH", "./chromedriver")
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)

        driver.get("https://kageherostudio.com/event/?event=daily")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "btn-login")))

        login_button = driver.find_element(By.CLASS_NAME, "btn-login")
        login_button.click()
        time.sleep(5)

        # Input email and password
        driver.find_element(By.CSS_SELECTOR, "#form-login > fieldset > div:nth-child(1) > input").send_keys(account['email'])
        driver.find_element(By.CSS_SELECTOR, "#form-login > fieldset > div:nth-child(2) > input").send_keys(account['password'])
        driver.find_element(By.CSS_SELECTOR, "#form-login > fieldset > div:nth-child(3) > button").click()
        time.sleep(10)

        try:
            claim_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#xexchange > div.reward-content.dailyClaim.reward-star"))
            )
            claim_button.click()
            time.sleep(5)
            item_information(driver, account['email'], account['server_name'])
        except Exception:
            logger.info("Item already claimed or unavailable.")
            item_information(driver, account['email'], account['server_name'])
        finally:
            driver.quit()

    except Exception as e:
        logger.error(f"Error during automation for {account['email']}: {e}")

# Main function
def main():
    accounts = load_accounts()
    if not accounts:
        logger.error("No accounts found. Check your environment variables.")
        return
    for account in accounts:
        claim_item_for_account(account)

if __name__ == "__main__":
    main()
