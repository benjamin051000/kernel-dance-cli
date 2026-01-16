import json
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def scrape_kernel_dance(commit):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        url = f"https://kernel.dance/#{commit}"
        driver.get(url)

        # Wait for body class to change from 'loading' to 'done' or 'error'
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.TAG_NAME, "body").get_attribute("class")
            in ["done", "error"]
        )

        # Get the output
        output = driver.find_element(By.ID, "output")
        result = output.text

        # Check if error
        if driver.find_element(By.TAG_NAME, "body").get_attribute("class") == "error":
            print(f"Error: {result}", file=sys.stderr)
            sys.exit(1)

        # Try to parse and pretty-print JSON
        try:
            data = json.loads(result)
            print(json.dumps(data, indent=2))
        except Exception:
            print(result)

    finally:
        driver.quit()


def main():
    if len(sys.argv) < 2:
        print("Usage: python kernel-dance.py <commit-sha>", file=sys.stderr)
        sys.exit(1)

    commit = sys.argv[1]
    scrape_kernel_dance(commit)


if __name__ == "__main__":
    main()
