import os
import json
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Load Environment Variables
load_dotenv()

# Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATA_JSON = os.getenv("DATA_JSON")

# Validate Environment Variables
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID or not DATA_JSON:
    raise EnvironmentError("❌ Variabel lingkungan tidak lengkap. Pastikan TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, dan DATA_JSON diatur.")

# Parse JSON to Accounts
try:
    ACCOUNTS = json.loads(DATA_JSON)
except json.JSONDecodeError:
    raise ValueError("❌ DATA_JSON tidak valid. Pastikan format JSON benar.")

# Function to send Telegram Notifications
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Gagal mengirim pesan Telegram: {e}")

# Setup Selenium Driver
def setup_driver():
    try:
        options = webdriver.FirefoxOptions()
        options.headless = True  # Mode headless agar tidak membuka GUI browser
        service = FirefoxService("/usr/local/bin/geckodriver")  # Path geckodriver
        return webdriver.Firefox(service=service, options=options)
    except Exception as e:
        raise RuntimeError(f"❌ Gagal menginisialisasi driver: {e}")

# Claim Process
def claim_rewards(account):
    username = account.get("username")
    password = account.get("password")
    server = account.get("server")

    if not username or not password or not server:
        send_telegram_message(f"⚠️ Data akun tidak lengkap: {account}")
        return

    driver = setup_driver()
    try:
        # Login Simulation
        send_telegram_message(f"🔄 Proses klaim dimulai untuk akun: {username}")
        driver.get("https://example.com/login")

        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "login-button").click()

        # Simulate claim process
        driver.get(f"https://example.com/server/{server}/claim")
        
        # Simulasi keberhasilan klaim
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
