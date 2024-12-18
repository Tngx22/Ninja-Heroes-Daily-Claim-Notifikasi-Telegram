import os
import logging
import asyncio
import cloudscraper
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram import Bot

# Constants
LOGIN_URL = 'https://kageherostudio.com/payment/server_.php'
EVENT_URL = 'https://kageherostudio.com/event/?event=daily'

USER_NAME = 'txtuserid'
PASS_NAME = 'txtpassword'
SRVR_POST = 'selserver'
REWARD_CLS = '.reward-star'

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Load Telegram bot credentials
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
bot = Bot(token=API_TOKEN)

# Load accounts from environment variables
def load_accounts():
    accounts = []
    for i in range(1, 21):  # 20 accounts max
        account = {
            "email": os.getenv(f"EMAIL{i}"),
            "password": os.getenv(f"PASSWORD{i}"),
            "server_name": os.getenv(f"SERVER_NAME{i}")
        }
        if all(account.values()):
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
        *🎉 CLAIM DETAILS 🎉*

━━━━━━━━━━━━━━━━━━━━━━━━

➤ *Claimed Day :* {claimed_day}
➤ *Reward Item :* {claimed_item}

━━━━━━━━━━━━━━━━━━━━━━━━

*🌐 Server     :* {server_name}
*📧 Email      :* {account_email}
"""

        asyncio.run(send_telegram_message(result_message))

    except Exception as e:
        logger.error(f"Error extracting item information: {e}")

# Function to claim item for a specific account
def claim_item_for_account(account):
    try:
        logger.info(f"Starting automation for account: {account['email']}")

        # Selenium WebDriver setup
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        driver_path = os.getenv("GECKODRIVER_PATH", "./drivers/geckodriver")
        service = FirefoxService(executable_path=driver_path)
        driver = webdriver.Firefox(service=service, options=options)

        scraper = cloudscraper.create_scraper(browser={'custom': 'firefox'})
        scraper.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

        # Login to the account
        driver.get(LOGIN_URL)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, USER_NAME))).send_keys(account['email'])
        driver.find_element(By.NAME, PASS_NAME).send_keys(account['password'])
        driver.find_element(By.NAME, SRVR_POST).send_keys(account['server_name'])
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Navigate to event page
        driver.get(EVENT_URL)

        # Claim reward
        try:
            claim_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, REWARD_CLS))
            )
            claim_button.click()
            logger.info(f"Reward claimed for account: {account['email']}")
            item_information(driver, account['email'], account['server_name'])
        except Exception as e:
            logger.error(f"Error claiming reward for {account['email']}: {e}")
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
