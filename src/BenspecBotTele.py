# BenspecBotTele.py

from datetime import datetime
import time
import requests
from PIL import Image
from shared_functions import setup_firefox_driver

# Telegram bot token and group ID
telegram_token = "your_telegram_token" #Edit your telegram account token here
telegram_group_id = "your_telegram_group_id" #Edit your group id where you sent the message

current_date = datetime.now().strftime("%Y-%m-%d")
message = f"[{current_date}] Unspec Today"

# Google Drive link
gdrive_link = "your_gdrive_link"

def main():
    driver = setup_firefox_driver(download_path=None, headless=True)
    driver.set_window_size(2066, 1068)

    try:
        driver.get(gdrive_link)
        time.sleep(3)

        # Capture full screenshot
        screenshot_path = "full_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"Full screenshot saved to {screenshot_path}")

        # Crop the image
        with Image.open(screenshot_path) as img:
            width, height = img.size
            cropped_img = img.crop((35, 145, width, height - 40))
            cropped_screenshot_path = "cropped_screenshot.png"
            cropped_img.save(cropped_screenshot_path)
            print(f"Cropped screenshot saved to {cropped_screenshot_path}")

        # Send the cropped image to Telegram
        telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendPhoto"
        with open(cropped_screenshot_path, "rb") as photo:
            response = requests.post(telegram_url, data={"chat_id": telegram_group_id}, files={"photo": photo})

        if response.status_code == 200:
            print("Screenshot successfully sent to Telegram.")
        else:
            print(f"Failed to send screenshot to Telegram. Error: {response.text}")

        # Send the message
        text_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        text_payload = {
            "chat_id": telegram_group_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        text_response = requests.post(text_url, data=text_payload)

        if text_response.status_code == 200:
            print("Message sent successfully")
        else:
            print(f"Failed to send message. Status code: {text_response.status_code}, Error: {text_response.text}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
