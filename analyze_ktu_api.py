#!/usr/bin/env python3
"""
Analyze KTU API calls by monitoring network requests
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

# Enable Network logging
capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options, desired_capabilities=capabilities)

try:
    print("Loading KTU website...")
    driver.get("https://ktu.edu.in/Menu/announcements")

    print("Waiting 10 seconds for API calls...")
    time.sleep(10)

    # Get network logs
    logs = driver.get_log("performance")

    print("\n=== Analyzing Network Requests ===")

    api_calls = []
    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if "Network.request" in log["method"] or "Network.response" in log["method"]:
            if "params" in log:
                if "request" in log["params"]:
                    url = log["params"]["request"].get("url", "")
                    if "api.ktu.edu.in" in url:
                        headers = log["params"]["request"].get("headers", {})
                        method = log["params"]["request"].get("method", "")
                        api_calls.append({
                            "url": url,
                            "method": method,
                            "headers": headers
                        })

    print(f"\nFound {len(api_calls)} API calls to api.ktu.edu.in")

    for i, call in enumerate(api_calls):
        print(f"\n--- API Call {i+1} ---")
        print(f"URL: {call['url']}")
        print(f"Method: {call['method']}")
        print("Headers:")
        for key, value in call['headers'].items():
            if key.lower() in ['authorization', 'x-api-key', 'token', 'bearer']:
                print(f"  {key}: {value}")

    # Also check if announcements API was called
    announcements_calls = [c for c in api_calls if 'announcement' in c['url'].lower()]
    if announcements_calls:
        print("\n=== Announcements API Calls ===")
        for call in announcements_calls:
            print(json.dumps(call, indent=2))

finally:
    driver.quit()
