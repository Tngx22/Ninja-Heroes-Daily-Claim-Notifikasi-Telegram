import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from datetime import datetime

# -------------------------
# KONFIGURASI LANGSUNG DI DALAM KODE
# -------------------------
TELEGRAM_BOT_TOKEN = "7518490579:AAFDdbjyO4u1L24ke76e_VSDUor-eAqkZgY"
TELEGRAM_CHAT_ID = "7997521757"
DATA_JSON = [
    {"username": "nhx4@sika3.com", "password": "asd1234", "server": 34},
    {"username": "nhx3@sika3.com", "password": "asd1234", "server": 34},
    {"username": "nhx2@sika3.com", "password": "asd1234", "server": 34},
    {"username": "nhtngx4@gmail.com", "password": "asd1234", "server": 34},
    {"username": "nhtngx3@gmail.com", "password": "asd1234", "server": 34},
    {"username": "nhtngx2@gmail.com", "password": "asd1234", "server": 34},
    {"username": "nhtngx1@gmail.com", "password": "asd1234", "server": 34},
    {"username": "nhx1@sika3.com", "password": "asd1234", "server": 34},
    {"username": "gacor1@gmail.com", "password": "gacor1", "server": 2},
    {"username": "tngxpoolunik@gmail.com", "password": "asd1234", "server": 34},
    {"username": "asd07@sika3.com", "password": "asd1234", "server": 34},
    {"username": "synxx1@sika3.com", "password": "asd1234", "server": 34},
    {"username": "test123@gmail.com", "password": "test123", "server": 1},
    {"username": "asd01@sika3.com", "password": "asd1234", "server": 34},
    {"username": "hantu2@gmail.com", "password": "hantu2", "server": 1},
    {"username": "hantu3@gmail.com", "password": "hantu3", "server": 1},
    {"username": "hantu1@gmail.com", "password": "hantu1", "server": 1},
    {"username": "hantu123@gmail.com", "password": "hantu123", "server": 9},
    {"username": "monyet1@gmail.com", "password": "monyet1", "server": 5},
    {"username": "naruto123@gmail.com", "password": "naruto123", "server": 24}
]
GECKODRIVER_PATH = "./drivers/geckodriver"

# -------------------------
# FUNGSI PENGIRIMAN PESAN TELEGRAM
# -------------------------
def send_telegram_message(message, parse_mode="HTML"):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": parse_mode}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ Pesan Telegram berhasil dikirim.")
    except requests.RequestException as e:
        print(f"❌ Gagal mengirim pesan Telegram: {e}")

# -------------------------
# KONFIGURASI SELENIUM
# -------------------------
def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = FirefoxService(GECKODRIVER_PATH)
    try:
        return webdriver.Firefox(service=service, options=options)
    except Exception as e:
        raise RuntimeError(f"❌ Gagal menginisialisasi WebDriver: {e}")

# -------------------------
# FUNGSI PROSES KLAIM HADIAH
# -------------------------
def claim_rewards(account):
    username = account.get("username")
    password = account.get("password")
    server = account.get("server")

    if not username or not password or not server:
        send_telegram_message(f"⚠️ <b>Data akun tidak lengkap</b>: {account}")
        return

    driver = setup_driver()
    try:
        send_telegram_message(f"🔄 <b>Memulai klaim hadiah</b>\n👤 <b>Akun</b>: {username}\n🖥️ <b>Server</b>: {server}")

        # Simulasi login
        driver.get("https://example.com/login")
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "login-button").click()

        # Simulasi klaim hadiah
        driver.get(f"https://example.com/server/{server}/claim")
        items = ["Item1", "Item2", "Item3"]  # Simulasi item yang diklaim
        item_list = "\n".join([f"• {item}" for item in items])

        # Notifikasi klaim berhasil
        send_telegram_message(
            f"🎉 <b>Klaim Berhasil</b>\n👤 <b>Akun</b>: {username}\n🖥️ <b>Server</b>: {server}\n🎁 <b>Item yang Diterima:</b>\n{item_list}\n\n🕒 <i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        )
    except Exception as e:
        send_telegram_message(f"❌ <b>Klaim Gagal</b>\n👤 <b>Akun</b>: {username}\n🖥️ <b>Server</b>: {server}\n🛑 <b>Error</b>: {str(e)}")
    finally:
        driver.quit()

# -------------------------
# EKSEKUSI UTAMA
# -------------------------
if __name__ == "__main__":
    send_telegram_message("🚀 <b>Proses Klaim Hadiah Dimulai</b>")
    for account in DATA_JSON:
        claim_rewards(account)
    send_telegram_message("✅ <b>Semua Klaim Hadiah Telah Selesai</b>\n🕒 <i>{}</i>".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
