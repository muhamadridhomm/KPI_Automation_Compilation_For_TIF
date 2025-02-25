# aqiDLFirefox.py

from datetime import datetime
import time
import os
from shared_functions import upload_to_drive, get_latest_downloaded_file, save_cookies, load_cookies, captcha_processor, setup_firefox_driver

# Constants
today = datetime.now().strftime("%Y-%m-%d")
cookie_file = "./data/cookiesaqi.pkl"
success_url = "https://access-quality.telkom.co.id/aqi/index.php/home"
login_url = f"https://access-quality.telkom.co.id/aqi/index.php/login"
download_url = f"https://access-quality.telkom.co.id/aqi/index.php/unspec/semesta/detail?regional=4&witel=MAGELANG&jenis=total_saldo&filter={today}"
user_name = "your_username"
pass_word = "your_password"

# Google Drive settings
SERVICE_ACCOUNT_FILE = 'witelmagelang-9ecb6346aadd.json'
FOLDER_ID = '1rEwGZq2bsfgi9XEtsIt9YbhRjXiwmrxX'

# Download directory
project_folder = os.path.abspath(os.getcwd())
download_path = os.path.join(project_folder, "downloads")
gecko_path = "/usr/local/bin/geckodriver"

# Ensure download directory exists
os.makedirs(download_path, exist_ok=True)

def login_attempt(driver):
    try:
        print("Attempting login...")
        driver.get(login_url)

        # Locate the captcha image
        captcha_element = driver.find_element(By.XPATH, "//img[contains(@src, '/assets/images/captcha')]")
        captcha_url = captcha_element.get_attribute("src")
        print(f"Captcha URL: {captcha_url}")

        # Download the captcha image
        captcha_image_path = "captcha.jpg"
        response = requests.get(captcha_url)
        if response.status_code == 200:
            with open(captcha_image_path, "wb") as file:
                file.write(response.content)
            print(f"Captcha saved as {captcha_image_path}")
        else:
            print("Failed to download captcha image")
            driver.quit()
            exit()

        captcha_image = captcha_processor(captcha_image_path)

        # Read text from the image
        reader = easyocr.Reader(['en'])
        result = reader.readtext(captcha_image, allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        captcha_text = "".join([detection[1] for detection in result])
        print(f"Captcha Text: {captcha_text}")

        # Enter credentials and captcha
        driver.find_element(By.ID, "username").send_keys(user_name)
        driver.find_element(By.ID, "password").send_keys(pass_word)
        driver.find_element(By.ID, "captcha").send_keys(captcha_text)

        time.sleep(1)

        # Submit the form
        login_button = driver.find_element(By.XPATH, "//button[@value='submit']")
        login_button.click()

        WebDriverWait(driver, 3).until(EC.url_to_be(success_url))
        print("Login successful!")
        return True

    except TimeoutException:
        print("Login failed. Retrying...")
        return False

def main():
    driver = setup_firefox_driver(download_path, headless=True)
    driver.get(login_url)
    load_cookies(driver, cookie_file)

    if not is_session_valid(driver):
        max_retries = 30
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
    driver.get(download_url)
    time.sleep(2)

    # Download button click
    dl_button = driver.find_element(By.XPATH, "//a[contains(@href, 'download_detail') and contains(text(), 'Download XLS')]")
    dl_button.click()

    time.sleep(4)
    latest_file = get_latest_downloaded_file(download_path)

    # File handling
    new_file_path = os.path.join(download_path, "Data Unspec Baru.xls")
    backup_file_path = os.path.join(download_path, "Data Unspec Lama.xls")
    output_file_path = os.path.join(download_path, "Data Ukur.txt")

    if os.path.exists(new_file_path):
        if os.path.exists(backup_file_path):
            os.remove(backup_file_path)
        os.rename(new_file_path, backup_file_path)

    shutil.move(latest_file, new_file_path)

    # Upload to Google Drive
    if latest_file:
        upload_to_drive(new_file_path, FOLDER_ID, "Data Unspec AQI.xlsx", SERVICE_ACCOUNT_FILE)
    else:
        print("No downloaded file found.")

    time.sleep(3)
    driver.quit()

if __name__ == "__main__":
    main()
