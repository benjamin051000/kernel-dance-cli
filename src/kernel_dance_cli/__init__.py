import json
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def scrape_kernel_dance(commit: str) -> str:
    options = Options()
    options.add_argument("--headless")

    with webdriver.Chrome(options=options) as driver:
        url = f"https://kernel.dance/#{commit}"
        driver.get(url)

        # Wait for body class to change from 'loading' to 'done' or 'error'
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.TAG_NAME, "body").get_attribute("class")
            in ["done", "error"]
        )

        output = driver.find_element(By.ID, "output")
        result = output.text

        if driver.find_element(By.TAG_NAME, "body").get_attribute("class") == "error":
            print(f"Error: {result}", file=sys.stderr)
            sys.exit(1)

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python kernel-dance.py <commit-sha>", file=sys.stderr)
        sys.exit(1)

    commit = sys.argv[1]
    result = scrape_kernel_dance(commit)

    try:
        data = json.loads(result)
    except json.JSONDecodeError:
        print(result)
    else:
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
