# shared_functions.py

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from PIL import Image, ImageEnhance
from selenium.webdriver.common.by import By
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import pandas as pd
import requests
import pickle
import time
import easyocr
import os
import shutil

def upload_to_drive(file_path, folder_id, new_file_name, service_account_file):
    """
    Uploads a file to Google Drive.

    Args:
        file_path (str): Path to the file to upload.
        folder_id (str): ID of the Google Drive folder to upload to.
        new_file_name (str): Name of the file to be uploaded.
        service_account_file (str): Path to the service account JSON file.
    """
    credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=['https://www.googleapis.com/auth/drive.file'])
    drive_service = build('drive', 'v3', credentials=credentials)

    existing_file_id = find_file_id(drive_service, new_file_name, folder_id)

    if existing_file_id:
        media = MediaFileUpload(file_path, mimetype='application/vnd.ms-excel')
        updated_file = drive_service.files().update(
            fileId=existing_file_id,
            media_body=media
        ).execute()
        print(f"File updated successfully. File ID: {updated_file.get('id')}")
    else:
        file_metadata = {
            'name': new_file_name,
            'parents': [folder_id],
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }
        media = MediaFileUpload(file_path, mimetype='application/vnd.ms-excel')
        new_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"File uploaded successfully with ID: {new_file.get('id')}")

def find_file_id(service, filename, folder_id):
    """
    Finds the file ID by name in a specific folder.

    Args:
        service: Google Drive service object.
        filename (str): Name of the file to find.
        folder_id (str): ID of the folder to search in.

    Returns:
        str: File ID if found, otherwise None.
    """
    query = f"name='{filename}' and '{folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id)").execute()
    items = results.get('files', [])
    return items[0]['id'] if items else None

def get_latest_downloaded_file(download_dir):
    """
    Gets the most recently downloaded file in the specified directory.

    Args:
        download_dir (str): Path to the download directory.

    Returns:
        str: Path to the most recently downloaded file.
    """
    files = os.listdir(download_dir)
    paths = [os.path.join(download_dir, f) for f in files]
    paths = [p for p in paths if os.path.isfile(p)]
    return max(paths, key=os.path.getmtime) if paths else None

def save_cookies(driver, filename):
    """
    Saves the browser cookies to a file.

    Args:
        driver: Selenium WebDriver instance.
        filename (str): Path to save the cookies.
    """
    with open(filename, "wb") as file:
        pickle.dump(driver.get_cookies(), file)
    print("Cookies saved.")

def load_cookies(driver, filename):
    """
    Loads the browser cookies from a file.

    Args:
        driver: Selenium WebDriver instance.
        filename (str): Path to load the cookies from.
    """
    try:
        with open(filename, "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print("Cookies loaded.")
    except FileNotFoundError:
        print("No saved cookies found.")

def captcha_processor(captcha_image_path, output_path="preprocessed_captchas.png"):
    """
    Processes a CAPTCHA image to enhance its readability for OCR.

    Args:
        captcha_image_path (str): Path to the original CAPTCHA image.
        output_path (str): Path to save the preprocessed CAPTCHA image.

    Returns:
        str: Path of the preprocessed CAPTCHA image.
    """
    try:
        captcha_image = Image.open(captcha_image_path)
        captcha_image = captcha_image.convert("L")
        enhancer = ImageEnhance.Contrast(captcha_image)
        captcha_image = enhancer.enhance(3.0)
        captcha_image.save(output_path)
        print(f"Captcha preprocessed and saved at {output_path}")
        return output_path
    except Exception as e:
        print(f"Error processing CAPTCHA: {e}")
        return None

def setup_firefox_driver(download_path, headless=True):
    """
    Sets up and returns a Firefox WebDriver instance.

    Args:
        download_path (str): Path to the download directory.
        headless (bool): Whether to run in headless mode.

    Returns:
        WebDriver: Configured Firefox WebDriver instance.
    """
    firefox_options = Options()
    firefox_options.set_preference("browser.download.folderList", 2)
    firefox_options.set_preference("browser.download.dir", download_path)
    firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.ms-excel")
    firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
    firefox_options.set_preference("pdfjs.disabled", True)
    firefox_options.set_preference("network.proxy.type", 0)
    if headless:
        firefox_options.add_argument('-headless')
    service = Service(gecko_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)
    return driver
