from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# === CONFIGURABLE INPUT ===
JOB_TITLE = "IT Support"
JOB_LOCATION = "Remote"

# === MAIN FUNCTION ===
def search_jobs(driver):
    print("Searching on https://www.indeed.com...")
    driver.get("https://www.indeed.com")

    wait = WebDriverWait(driver, 15)

    # Wait for job title input (WHAT)
    what_input = wait.until(EC.presence_of_element_located((By.ID, "text-input-what")))
    what_input.clear()
    what_input.send_keys(JOB_TITLE)

    # Wait for location input (WHERE)
    where_input = wait.until(EC.presence_of_element_located((By.ID, "text-input-where")))
    where_input.clear()
    where_input.send_keys(JOB_LOCATION)

    # Submit search
    where_input.send_keys(Keys.RETURN)
    print(f"Search triggered for '{JOB_TITLE}' in '{JOB_LOCATION}'.")

    # Optional: wait for results to load
    time.sleep(5)

    # TODO: Next steps: Scrape job listings, auto-apply logic, saving jobs to tracker, etc.

# === ENTRY POINT ===
def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")  # Uncomment to hide browser window

    service = Service()  # Will auto-find chromedriver
    driver = webdriver.Chrome(service=service, options=options)

    try:
        search_jobs(driver)
    finally:
        input("Press Enter to close the browser...")
        driver.quit()

if __name__ == "__main__":
    main()
