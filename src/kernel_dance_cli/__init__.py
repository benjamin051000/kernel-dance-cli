import json
import sys
from contextlib import contextmanager
from pathlib import Path

from selenium import webdriver
from selenium.common import SessionNotCreatedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

__all__ = ["scrape_kernel_dance"]


@contextmanager
def pick_webdriver():
    """Choose a webdriver based on the ones your system has installed."""
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
    except SessionNotCreatedException:
        # Chrome not available. Try Firefox
        try:
            # On Ubuntu, firefox is usually installed as a snap...
            if Path("/snap/bin/geckodriver").exists():
                service = webdriver.FirefoxService(
                    executable_path="/snap/bin/geckodriver"
                )
            else:
                # But sometimes as a deb.
                service = None

            ff_options = webdriver.FirefoxOptions()
            ff_options.add_argument("--headless")
            driver = webdriver.Firefox(options=ff_options, service=service)

        except SessionNotCreatedException:
            print("Well, you need to install a webdriver.", file=sys.stderr)
            sys.exit(1)

    yield driver

    driver.quit()


def scrape_kernel_dance(commit: str) -> str:
    with pick_webdriver() as driver:
        url = f"https://kernel.dance/#{commit}"
        driver.get(url)

        # Wait for body class to change from 'loading' to 'done' or 'error'
        try:
            WebDriverWait(driver, 10).until(
                lambda d: d.find_element(By.TAG_NAME, "body").get_attribute("class")
                in ["done", "error"]
            )
        except TimeoutException:
            print(f"Error: Timed out while trying to access {url}.", file=sys.stderr)
            sys.exit(1)

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
