import os
import json
import time
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException

# Load Environment Variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATA_JSON = os.getenv("DATA_JSON")

# Parse Account Data
try:
    ACCOUNTS = json.loads(DATA_JSON)
except json.JSONDecodeError:
    print("❌ Gagal membaca DATA_JSON. Format JSON salah.")
    exit(1)

# Function to send Telegram Notifications
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"⚠️ Gagal mengirim notifikasi Telegram: {e}")

# Setup Selenium Driver with Headless Firefox
def setup_driver():
    options = Options()
    options.headless = True  # Mode headless untuk CI/CD
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service("/usr/local/bin/geckodriver")
    try:
        driver = webdriver.Firefox(service=service, options=options)
        return driver
    except WebDriverException as e:
        send_telegram_message(f"❌ Gagal inisialisasi Selenium: {e}")
        exit(1)

# Login and Claim Rewards
def claim_rewards(account):
    username = account["username"]
    password = account["password"]
    server = account["server"]
    driver = setup_driver()

    try:
        # Buka halaman login
        send_telegram_message(f"🔄 Memulai klaim untuk akun {username}...")
        driver.get("https://example.com/login")
        time.sleep(2)  # Beri waktu halaman dimuat

        # Input username dan password
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "login-button").click()
        time.sleep(3)

        # Verifikasi login berhasil
        if "dashboard" not in driver.current_url:  # Sesuaikan URL dashboard yang benar
            send_telegram_message(f"⚠️ Login gagal untuk akun {username}. Periksa kredensial.")
            return

        # Proses klaim reward
        driver.get(f"https://example.com/server/{server}/claim")
        time.sleep(2)

        # Verifikasi klaim sukses (ubah selektor sesuai notifikasi klaim)
        try:
            success_message = driver.find_element(By.CLASS_NAME, "claim-success").text
            send_telegram_message(f"🎉 Klaim berhasil untuk akun: {username} di server {server}!\n{success_message}")
        except NoSuchElementException:
            send_telegram_message(f"❌ Klaim gagal untuk akun {username}. Notifikasi klaim tidak ditemukan.")

    except (NoSuchElementException, TimeoutException) as e:
        send_telegram_message(f"❌ Klaim gagal untuk akun {username} - Error: {e}")
    except Exception as e:
        send_telegram_message(f"❌ Terjadi kesalahan pada akun {username}: {e}")
    finally:
        driver.quit()

# Main Execution
if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID or not DATA_JSON:
        print("❌ Variabel lingkungan tidak lengkap. Pastikan TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, dan DATA_JSON diatur.")
        exit(1)

    send_telegram_message("🚀 Memulai proses klaim untuk semua akun...")
    for account in ACCOUNTS:
        claim_rewards(account)
    send_telegram_message("✅ Proses klaim selesai untuk semua akun!")
