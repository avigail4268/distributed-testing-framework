# File: smart_worker.py
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# The address of our central server
SERVER_URL = "http://host.docker.internal:8080"


def run_smart_worker():
    print("--- Worker Started: Asking server for a task ---")

    # 1. Ask the server for a task
    try:
        response = requests.get(f"{SERVER_URL}/get-task")
        task_data = response.json()
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        return

    # Check if the server said there are no tasks left
    if "message" in task_data and task_data["message"] == "no_tasks_available":
        print("No tasks available. Worker is going to sleep.")
        return

    # Extract the dynamic data from the server's response
    task_id = task_data["task_id"]
    target_url = task_data["target_url"]
    category = task_data["category"]
    expected_product = task_data["expected_product"]

    print(f"Received Task {task_id}: Test category '{category}' for expected product '{expected_product}'")
    # 2. Setup Browser (Updated for Docker / Headless)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run without a physical window
    options.add_argument('--no-sandbox')  # Bypass OS security model (needed in Docker)
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 10)

    start_time = time.time()
    status = "FAILED"
    error_msg = ""
    try:
        # 3. Run the automation using the dynamic data
        driver.get(target_url)

        category_element = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, category)))
        category_element.click()

        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#tbodyid .card-title a"), expected_product))

        first_product = driver.find_element(By.CSS_SELECTOR, "#tbodyid .card-title a").text

        assert first_product == expected_product, f"Expected '{expected_product}', got '{first_product}'"

        print(f"Task {task_id} completed successfully!")
        status = "PASSED"

    except Exception as e:
        print(f"Task {task_id} failed: {e}")
        error_msg = str(e)

    finally:
        driver.quit()
        end_time = time.time()
        duration = round(end_time - start_time, 2)

        # 4. Send the result back to the server via POST request
        print(f"--- Sending results back to server (Duration: {duration}s) ---")
        result_payload = {
            "task_id": task_id,
            "status": status,
            "duration_seconds": duration,
            "error_message": error_msg if error_msg else ""
        }

        requests.post(f"{SERVER_URL}/submit-result", json=result_payload)
        print("Result submitted successfully!")


if __name__ == "__main__":
    run_smart_worker()