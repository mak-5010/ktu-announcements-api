#!/usr/bin/env python3
# ktu_scrape_site.py
"""
Scrape announcements from https://ktu.edu.in/Menu/announcements using Selenium.
Saves output to ktu_announcements.json.

Requirements:
  pip install selenium webdriver-manager beautifulsoup4 requests
  Chrome/Chromium installed
"""

import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import sys
import os

KTU_URL = "https://ktu.edu.in/Menu/announcements"
OUTPUT_FILE = "ktu_announcements.json"
WAIT_SECONDS = 35  # wait for JS-rendered content (increased for Render)
HEADLESS = True    # set False while debugging to see the browser

def make_driver(headless=HEADLESS):
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    # Modern headless
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # reduce logging
    chrome_options.add_argument("--log-level=3")
    # Memory optimization for low-RAM environments (Render free tier = 512MB)
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")  # Don't load images to save memory
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    # Note: --single-process removed as it can cause Chrome to crash
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--metrics-recording-only")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    # Additional stability flags for low-memory environments
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    # set a realistic user-agent
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def wait_for_announcements(driver):
    """Wait until announcements are present in the DOM (multiple fallbacks)."""
    wait = WebDriverWait(driver, WAIT_SECONDS)
    # Try a few XPaths that match common announcement elements
    try:
        wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(@class,'announcement')] | //div[contains(@class,'card') and .//h4] | //h4/a"
            ))
        )
        return True
    except TimeoutException:
        return False

def extract_attachments_from_block(block):
    attachments = []
    try:
        # find anchors that are likely attachments
        anchors = block.find_elements(By.XPATH, ".//a[contains(@href,'/eu/att/') or contains(text(),'Notification') or contains(text(),'Circular') or contains(@href,'att') or contains(@href,'/eu/') ]")
        for a in anchors:
            href = a.get_attribute("href")
            text = a.text.strip()
            if href:
                attachments.append({"title": text or os.path.basename(href), "href": href})
    except Exception:
        pass
    return attachments

def extract_from_dom(driver):
    results = []
    # Prefer structured blocks (announcement class or cards)
    blocks = driver.find_elements(By.XPATH, "//div[contains(@class,'announcement')] | //div[contains(@class,'card') and .//h4]")

    # If none found, fallback to h4/a anchors
    if not blocks:
        anchors = driver.find_elements(By.XPATH, "//h4/a | //div[@class='content']//a[contains(@href,'/eu/att') or contains(@href,'notification') or contains(@href,'notification')]")
        for a in anchors:
            try:
                title = a.text.strip()
                href = a.get_attribute("href")
                # Attempt to find sibling date or message
                parent = a.find_element(By.XPATH, "./ancestor::div[1]")
                date = ""
                try:
                    date_el = parent.find_element(By.XPATH, ".//span[contains(@class,'date')] | .//p[contains(@class,'date')] | .//small")
                    date = date_el.text.strip()
                except Exception:
                    pass
                msg_html = ""
                try:
                    msg = parent.find_element(By.XPATH, ".//p")
                    msg_html = msg.get_attribute("innerHTML")
                except Exception:
                    pass
                attachments = extract_attachments_from_block(parent)
                results.append({
                    "title": title,
                    "link": href,
                    "date": date,
                    "message_html": msg_html,
                    "attachments": attachments
                })
            except Exception:
                continue
        return results

    # Parse each block
    for b in blocks:
        try:
            title = ""
            link = ""
            # Title typically in h4 > a
            try:
                title_el = b.find_element(By.XPATH, ".//h4/a")
                title = title_el.text.strip()
                link = title_el.get_attribute("href") or ""
            except NoSuchElementException:
                # fallback: first anchor in block
                try:
                    a = b.find_element(By.XPATH, ".//a[1]")
                    title = a.text.strip()
                    link = a.get_attribute("href") or ""
                except Exception:
                    title = ""
                    link = ""
            # Date
            date_text = ""
            try:
                date_el = b.find_element(By.XPATH, ".//span[contains(@class,'date')] | .//p[contains(@class,'date')] | .//small | .//h4/following-sibling::*[1]")
                date_text = date_el.text.strip()
            except Exception:
                # maybe date sits in a different small tag
                try:
                    date_el = b.find_element(By.XPATH, ".//p[contains(@class,'announcementDate')]")
                    date_text = date_el.text.strip()
                except Exception:
                    date_text = ""

            # Message HTML (first <p> or div.message)
            message_html = ""
            try:
                msg_el = b.find_element(By.XPATH, ".//div[contains(@class,'message')] | .//p")
                message_html = msg_el.get_attribute("innerHTML").strip()
            except Exception:
                message_html = ""

            # attachments
            attachments = extract_attachments_from_block(b)

            results.append({
                "title": title,
                "link": link,
                "date": date_text,
                "message_html": message_html,
                "attachments": attachments
            })
        except Exception as e:
            # ignore block parse errors but log to stdout
            print("Parse error for block:", e)
            continue

    return results

def main():
    driver = make_driver(headless=HEADLESS)
    try:
        print("Loading:", KTU_URL)
        driver.get(KTU_URL)

        # Let initial JS run
        time.sleep(3)  # Increased from 1 to 3 seconds for slower servers

        ok = wait_for_announcements(driver)
        if not ok:
            print("Timed out waiting for announcement elements. Trying a longer wait + scroll.")
            # try scroll and longer wait
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Increased wait time
            if not wait_for_announcements(driver):
                print("No announcements found after extended wait.")
                # Log page title for debugging
                print("Page title:", driver.title)
                # still attempt extraction (may be partial)
        # extract
        announcements = extract_from_dom(driver)
        print("Found announcements:", len(announcements))

        # If empty, as a last resort try to fetch the HTML content (page source) and parse for 'announcement' keyword
        if not announcements:
            page_source = driver.page_source
            print("Checking page source length:", len(page_source))
            if "Announcement" in page_source or "announcement" in page_source.lower():
                print("Found keyword in page source; attempting fallback BeautifulSoup parse of static HTML.")
                soup = BeautifulSoup(page_source, "html.parser")
                fallback = []

                # Parse KTU-specific structure: div.row.m-b-25 containing announcements
                announcement_blocks = soup.select("div.row.m-b-25")
                print(f"Found {len(announcement_blocks)} announcement blocks")

                for block in announcement_blocks:
                    try:
                        # Title is in h6.f-w-bold
                        title_el = block.select_one("h6.f-w-bold")
                        title = title_el.get_text(strip=True) if title_el else ""

                        # Date is in div.text-theme.h6.m-t-10.f-w-bold
                        date_el = block.select_one("div.text-theme.h6.m-t-10.f-w-bold")
                        date = date_el.get_text(strip=True).replace("", "").strip() if date_el else ""

                        # Message is in div.m-t-10.font-14 > p
                        msg_el = block.select_one("div.m-t-10.font-14")
                        message_html = str(msg_el) if msg_el else ""
                        message_text = msg_el.get_text(strip=True) if msg_el else ""

                        # Attachments - button with value attribute
                        attachments = []
                        button = block.select_one("button.btn")
                        if button and button.get("value"):
                            attachments.append({
                                "title": button.get_text(strip=True).replace("", "").strip(),
                                "href": f"#attachment-{button.get('value')}"  # KTU uses encoded values
                            })

                        if title:  # Only add if we have a title
                            fallback.append({
                                "title": title,
                                "link": "",  # KTU doesn't provide direct links in this structure
                                "date": date,
                                "message_html": message_html,
                                "message_text": message_text,
                                "attachments": attachments
                            })
                    except Exception as e:
                        print(f"Error parsing announcement block: {e}")
                        continue

                print(f"Fallback parsed {len(fallback)} announcements")

                # Debug: print sample of page source if nothing found
                if len(fallback) == 0:
                    print("DEBUG: First 500 chars of page source:")
                    print(page_source[:500])

                announcements = fallback
            else:
                print("No announcement keywords found in page source")
                print("DEBUG: Page source sample:", page_source[:300])

        # sanitize message_html -> message_text
        for item in announcements:
            mh = item.get("message_html", "") or ""
            item["message_text"] = BeautifulSoup(mh, "html.parser").get_text(separator="\n").strip()

        result = {
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "count": len(announcements),
            "announcements": announcements
        }

        # Save JSON
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("Saved", OUTPUT_FILE)

        # OPTIONAL: POST to your WordPress endpoint (uncomment and configure)
        # wp_endpoint = "https://your-site.com/wp-json/yourplugin/v1/ktu-sync"
        # try:
        #     resp = requests.post(wp_endpoint, json=result, timeout=15)
        #     print("Posted to WP:", resp.status_code, resp.text)
        # except Exception as e:
        #     print("Failed to POST to WP:", e)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
