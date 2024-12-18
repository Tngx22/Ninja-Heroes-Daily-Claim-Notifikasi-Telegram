import os
import json
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from datetime import datetime

# Load Environment Variables
load_dotenv()

# Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATA_JSON = os.getenv("DATA_JSON")
GECKODRIVER_PATH = os.getenv("GECKODRIVER_PATH", "/usr/local/bin/geckodriver")

# Validate Environment Variables
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID or not DATA_JSON or not GECKODRIVER_PATH:
    raise EnvironmentError("❌ Variabel lingkungan tidak lengkap. Pastikan TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, DATA_JSON, dan GECKODRIVER_PATH diatur dengan benar.")

# Parse JSON Data to Accounts
try:
    ACCOUNTS = json.loads(DATA_JSON)
except json.JSONDecodeError:
    raise ValueError("❌ DATA_JSON tidak valid. Pastikan format JSON benar.")

# Function to send Telegram notifications
def send_telegram_message(message, parse_mode="Markdown"):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": parse_mode}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Gagal mengirim pesan Telegram: {e}")

# Function to setup Selenium WebDriver
def setup_driver():
    options = Options()
    options.add_argument("--headless")  # Enable headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = FirefoxService(GECKODRIVER_PATH)
    try:
        return webdriver.Firefox(service=service, options=options)
    except Exception as e:
        raise RuntimeError(f"❌ Gagal menginisialisasi WebDriver: {e}")

# Function to handle login and claim process
def claim_rewards(account):
    username = account.get("username")
    password = account.get("password")
    server = account.get("server")

    if not username or not password or not server:
        send_telegram_message(f"⚠️ *Data akun tidak lengkap:*\n`{json.dumps(account, indent=2)}`")
        return

    driver = setup_driver()
    try:
        # Simulate login process
        send_telegram_message(f"🔄 *Memulai klaim untuk akun:*\n`{username}`")
        driver.get("https://example.com/login")

        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "login-button").click()

        # Navigate to claim URL
        claim_url = f"https://example.com/server/{server}/claim"
        driver.get(claim_url)

        # Simulate item collection
        claimed_items = driver.find_element(By.ID, "claimed-items").text  # Replace with actual element
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Success notification
        send_telegram_message(
            f"🎉 *Klaim berhasil untuk akun:* `{username}`\n"
            f"📅 *Server:* `{server}`\n"
            f"🕒 *Waktu:* `{timestamp}`\n\n"
            f"🎁 *Item yang diterima:*\n```{claimed_items}```"
        )
    except Exception as e:
        send_telegram_message(f"❌ *Klaim gagal untuk akun:* `{username}`\n🛑 *Error:* `{str(e)}`")
    finally:
        driver.quit()

# Main Execution
if __name__ == "__main__":
    send_telegram_message("🚀 *Memulai proses klaim untuk semua akun...*", parse_mode="Markdown")
    for account in ACCOUNTS:
        claim_rewards(account)
    send_telegram_message("✅ *Proses klaim selesai untuk semua akun!*", parse_mode="Markdown")
