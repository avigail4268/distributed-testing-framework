# File: basic_test.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def run_basic_automation_test():
    """
    Runs a basic automated test on a demo e-commerce site.
    Validates that the 'Monitors' category displays the correct first product.
    """
    target_url = "https://www.demoblaze.com/"

    # --- 1. Browser Initialization ---
    print("--- Starting test: Opening Chrome browser... ---")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)
    test_passed = False

    try:
        # --- 2. Navigate to target URL ---
        print(f"Navigating to: {target_url}")
        driver.get(target_url)

        # --- 3. Locate elements and perform actions ---
        print("Searching for 'Monitors' category...")
        monitors_category = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Monitors")))
        monitors_category.click()
        print("Clicked on 'Monitors' category.")

        # --- 4. Assertion (The actual verification) - UPDATED! ---
        print("Waiting for the products grid to update (AJAX call)...")
        expected_product = "Apple monitor 24"

        # Here is the magic: We explicitly wait for the specific text to appear
        # in the first product card, so we know the category actually changed!
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#tbodyid .card-title a"), expected_product))

        # Now it's safe to grab the element
        first_product_title = driver.find_element(By.CSS_SELECTOR, "#tbodyid .card-title a")
        product_name = first_product_title.text

        print(f"First product found: {product_name}")
        assert product_name == expected_product, f"Error! Expected '{expected_product}', but got '{product_name}'"

        print("--- Test passed successfully! ---")
        test_passed = True

    except Exception as e:
        print(f"*** Test failed! Error: {str(e)} ***")
        test_passed = False
    finally:
        # --- 5. Clean up ---
        print("Closing browser.")
        driver.quit()


if __name__ == "__main__":
    run_basic_automation_test()