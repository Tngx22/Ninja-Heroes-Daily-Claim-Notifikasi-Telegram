import os
import json
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options

# Load Environment Variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATA_JSON = os.getenv("DATA_JSON")
ACCOUNTS = json.loads(DATA_JSON)

# Function to send Telegram Notifications
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

# Setup Selenium Driver with Headless Mode
def setup_driver():
    options = Options()
    options.headless = True  # Aktifkan mode headless
    options.add_argument("--no-sandbox")  # Tambahan untuk lingkungan CI/CD
    options.add_argument("--disable-dev-shm-usage")  # Hindari shared memory issue
    service = Service("/usr/local/bin/geckodriver")  # Path ke Geckodriver
    return webdriver.Firefox(service=service, options=options)

# Claim Process
def claim_rewards(account):
    username = account["username"]
    password = account["password"]
    server = account["server"]
    driver = setup_driver()
    try:
        # Simulasi Login (Gantilah URL dan selektor sesuai kebutuhan)
        driver.get("https://example.com/login")
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "login-button").click()

        # Simulasi Proses Klaim
        driver.get(f"https://example.com/server/{server}/claim")
        # Jika klaim berhasil, kirim notifikasi
        send_telegram_message(f"🎉 Klaim berhasil untuk akun: {username} di server {server} 🎮")
    except Exception as e:
        send_telegram_message(f"❌ Klaim gagal untuk akun: {username} - Error: {str(e)}")
    finally:
        driver.quit()

# Main Execution
if __name__ == "__main__":
    send_telegram_message("🚀 Memulai proses klaim untuk semua akun...")
    for account in ACCOUNTS:
        claim_rewards(account)
    send_telegram_message("✅ Proses klaim selesai untuk semua akun!")
