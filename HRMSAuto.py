import os
import time
import schedule
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

EMAIL = os.getenv("HRMS_EMAIL")
PASSWORD = os.getenv("HRMS_PASSWORD")
URL = os.getenv("HRMS_URL")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "C:\\chromedriver\\chromedriver-win64\\chromedriver.exe")

def login_logout():
    print("Launching HRMS automation...")

    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)

    try:
        driver.get(URL)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "txtUserName"))).send_keys(EMAIL)
        driver.find_element(By.ID, "txtPassword").send_keys(PASSWORD)

        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[contains(@src, 'recaptcha')]"))
        )
        captcha = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "recaptcha-checkbox-border"))
        )
        captcha.click()
        driver.switch_to.default_content()

        time.sleep(3)
        driver.find_element(By.ID, "btnLogin").click()

        try:
            moved_link = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//a[text()='here']"))
            )
            redirect_url = moved_link.get_attribute("href")
            if redirect_url:
                print(f"Redirecting to: {redirect_url}")
                driver.get(redirect_url)
        except:
            print("No redirect link — assuming login was successful.")

        try:
            close_modal = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//span[@aria-hidden='true' and text()='×']"))
            )
            close_modal.click()
        except:
            print("No popup modal to close.")

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Sign In / Out"))
        ).click()

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "MainContent_Button_Sign"))
        ).click()

        print("Sign In/Out action completed successfully.")

    except Exception as e:
        print(f"Automation error: {e}")
    finally:
        time.sleep(2)
        driver.quit()

schedule.every().day.at("09:00").do(login_logout)
schedule.every().day.at("22:37").do(login_logout)

print("HRMS Bot is running... Waiting for scheduled times (09:00 & 22:37)")
while True:
    schedule.run_pending()
    time.sleep(30)
