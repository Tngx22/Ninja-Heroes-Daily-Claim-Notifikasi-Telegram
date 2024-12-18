import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import random

# Konfigurasi driver
GECKODRIVER_PATH = os.environ.get("GECKODRIVER_PATH")
TELEGRAM_API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
options = Options()
options.add_argument("--headless")  # Mode tanpa tampilan browser
service = Service(GECKODRIVER_PATH)

# Fungsi untuk mengirim notifikasi Telegram
def send_telegram_notification(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"  # Agar bisa menggunakan format teks Telegram
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("INFO - Telegram notification sent successfully.")
        else:
            print(f"ERROR - Failed to send Telegram notification. Status code: {response.status_code}")
    except Exception as e:
        print(f"ERROR - Exception while sending Telegram notification: {str(e)}")

# Fungsi untuk memilih pesan acak yang menarik
def get_random_success_message(account_name, items):
    success_messages = [
        f"🎉 *Selamat!* Rewards berhasil diklaim untuk akun *{account_name}*!\n📦 Item yang didapatkan: *{items}*.\nTetap semangat, klaim lagi di kesempatan berikutnya! 🚀",
        f"🔥 *Mantap!* Klaim berhasil untuk akun *{account_name}*.\n🎁 Item reward: *{items}*.\nAyo lanjutkan perjalanannya! 💪",
        f"💎 *Boom!* Rewards untuk akun *{account_name}* sukses diklaim!\n✨ Kamu mendapatkan: *{items}*.\nSampai jumpa di klaim berikutnya! 🌟",
        f"🌟 *Horee!* Klaim sukses untuk akun *{account_name}*!\n🎊 Item hadiah: *{items}*.\nTeruslah menjadi sang pemenang! 🏆",
    ]
    return random.choice(success_messages)

def get_random_failure_message(account_name, error_message):
    failure_messages = [
        f"⏰ *Oops!* Klaim gagal untuk akun *{account_name}*.\n🚨 Alasan: *{error_message}*.\nCoba lagi lain waktu, ya! 💡",
        f"❌ *Gagal!* Klaim reward untuk akun *{account_name}* tidak berhasil.\n🔍 Error: *{error_message}*.\nJangan menyerah, ya! 🔄",
        f"😓 *Yahh!* Klaim gagal di akun *{account_name}*.\n⚠️ Penyebab: *{error_message}*.\nAyo coba lagi nanti! 🔧",
    ]
    return random.choice(failure_messages)

# Fungsi utama untuk klaim reward
def claim_reward(email, password, server_name):
    driver = webdriver.Firefox(service=service, options=options)
    wait = WebDriverWait(driver, 10)  # Tunggu elemen dengan timeout 10 detik
    try:
        print(f"INFO - Starting automation for account: {server_name}")
        
        # Akses halaman login
        driver.get("https://example.com/login")

        # Input email
        email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_input.send_keys(email)

        # Input password
        password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_input.send_keys(password)

        # Klik tombol login
        login_button = wait.until(EC.element_to_be_clickable((By.ID, "login-button")))
        login_button.click()

        # Tunggu halaman dashboard atau reward
        dashboard = wait.until(EC.presence_of_element_located((By.ID, "dashboard")))
        print(f"SUCCESS - Login successful for account: {server_name}")

        # Proses klaim reward (simulasi)
        reward_button = wait.until(EC.element_to_be_clickable((By.ID, "claim-reward")))
        reward_button.click()

        # Simulasi nama item reward
        items_claimed = "100 Gold Coins, 5 Rare Gems, 1 Mega Booster"

        print(f"SUCCESS - Rewards claimed for account: {server_name}")
        
        # Kirim notifikasi Telegram jika sukses
        success_message = get_random_success_message(server_name, items_claimed)
        send_telegram_notification(success_message)

    except TimeoutException:
        error_message = "Timeout saat memuat halaman"
        print(f"ERROR - {error_message} for account: {server_name}")
        driver.save_screenshot("error.png")
        failure_message = get_random_failure_message(server_name, error_message)
        send_telegram_notification(failure_message)
    except NoSuchElementException:
        error_message = "Elemen tidak ditemukan"
        print(f"ERROR - {error_message} for account: {server_name}")
        driver.save_screenshot("error.png")
        failure_message = get_random_failure_message(server_name, error_message)
        send_telegram_notification(failure_message)
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        print(f"ERROR - {error_message} for account: {server_name}")
        driver.save_screenshot("error.png")
        failure_message = get_random_failure_message(server_name, error_message)
        send_telegram_notification(failure_message)
    finally:
        driver.quit()

# Loop untuk banyak akun
for i in range(1, 21):  # Loop dari EMAIL1 sampai EMAIL20
    email = os.environ.get(f"EMAIL{i}")
    password = os.environ.get(f"PASSWORD{i}")
    server_name = os.environ.get(f"SERVER_NAME{i}")

    if email and password and server_name:
        claim_reward(email, password, server_name)
    else:
        print(f"INFO - No credentials found for account {i}, skipping...")
