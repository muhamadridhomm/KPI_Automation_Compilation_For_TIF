# iBoosterUkr.py

from datetime import datetime
import time
import os
from shared_functions import upload_to_drive, get_latest_downloaded_file, save_cookies, load_cookies, captcha_processor, setup_firefox_driver

# Constants
cookie_file = "./data/cookiesbooster.pkl"
start_url = "https://dbaccess-ibooster.telkom.co.id"
success_url = "https://dbaccess-ibooster.telkom.co.id/ibooster/home.php"
login_url = "https://dbaccess-ibooster.telkom.co.id/login/"
download_url = f"https://dbaccess-ibooster.telkom.co.id/ibooster/home.php?page=PG336"
user_name = "your_username"
pass_word = "your_password"

# Google Drive settings
SERVICE_ACCOUNT_FILE = 'witelmagelang-9ecb6346aadd.json'
FOLDER_ID = '1rEwGZq2bsfgi9XEtsIt9YbhRjXiwmrxX'

# Download directory
project_folder = os.path.abspath(os.getcwd())
download_path = os.path.join(project_folder, "downloads")

def login_attempt(driver):
    try:
        print("Attempting login...")
        driver.get(login_url)
        time.sleep(2)

        # Locate the captcha image
        captcha_element = driver.find_element(By.XPATH, "//img[@alt='gambar']")
        captcha_element.screenshot("captchabooster.jpg")

        # Process the captcha
        captcha_image = captcha_processor("captchabooster.jpg")

        # Read text from the image
        reader = easyocr.Reader(['en'])
        result = reader.readtext(captcha_image, allowlist='0123456789abcdefghijklmnofpqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        captcha_text = "".join([detection[1] for detection in result])
        print(f"Captcha Text: {captcha_text}")

        # Enter credentials and captcha
        driver.find_element(By.ID, "username").send_keys(user_name)
        driver.find_element(By.ID, "password").send_keys(pass_word)
        driver.find_element(By.NAME, "captcha").send_keys(captcha_text)

        time.sleep(1)

        # Submit the form
        login_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Log in']")
        login_button.click()

        time.sleep(2)
        print("Login successful!")
        return True

    except TimeoutException:
        print("Login failed. Retrying...")
        return False

def main():
    driver = setup_firefox_driver(download_path, headless=True)
    driver.get(start_url)
    load_cookies(driver, cookie_file)

    if not is_session_valid(driver):
        max_retries = 20
        for attempt in range(max_retries):
            print(f"Attempt {attempt + 1} of {max_retries}")
            if login_attempt(driver):
                break
            if attempt < max_retries - 1:
                time.sleep(2)
        else:
            print("All login attempts failed.")
    else:
        print("Accessing the home page. Session is already active.")

    save_cookies(driver, cookie_file)

    # Access download URL
   
