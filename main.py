from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import os

# Streamlit app URLs from environment variables (or defaults)
STREAMLIT_URLS = [
    os.environ.get("STREAMLIT_APP_URL_1", "https://mbireceipt.streamlit.app/"),
    os.environ.get("STREAMLIT_APP_URL_2", "https://gan-or-template.streamlit.app/"),
]

def main():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        for url in STREAMLIT_URLS:
            driver.get(url)
            print(f"Opened {url}")

            # Use contains(., ...) instead of contains(text(), ...) so it also
            # matches button labels that are wrapped in a nested <span>/<div>,
            # which contains(text(), ...) silently misses.
            BUTTON_XPATH = "//button[contains(., 'Yes, get this app back up')]"

            wait = WebDriverWait(driver, 30)  # give slower cold-starts more time
            try:
                # Look for the wake-up button
                button = wait.until(
                    EC.presence_of_element_located((By.XPATH, BUTTON_XPATH))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                button = wait.until(EC.element_to_be_clickable((By.XPATH, BUTTON_XPATH)))
                print("Wake-up button found. Clicking...")
                button.click()

                # After clicking, check if it disappears
                try:
                    wait.until(EC.invisibility_of_element_located((By.XPATH, BUTTON_XPATH)))
                    print(f"Button clicked and disappeared ✅ ({url} should be waking up)")
                except TimeoutException:
                    print(f"Button was clicked but did NOT disappear ❌ (possible failure on {url})")

            except TimeoutException:
                # No button at all → app is assumed to be awake
                print(f"No wake-up button found. Assuming app is already awake ✅ ({url})")

    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)
    finally:
        driver.quit()
        print("Script finished.")

if __name__ == "__main__":
    main()
