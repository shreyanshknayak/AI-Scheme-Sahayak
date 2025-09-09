from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time

# Setup Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(service=Service("chromedriver-mac-arm64/chromedriver"), options=options)

driver.get("https://www.myscheme.gov.in/search")
time.sleep(3)

scheme_list = []
seen_links = set()
MAX_PAGES = 100

def extract_scheme_links():
    try:
        # Wait for scheme cards/links to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href^='/schemes/']"))
        )

        links = driver.find_elements(By.CSS_SELECTOR, "a[href^='/schemes/']")
        for link in links:
            href = link.get_attribute("href")
            text = link.text.strip()

            if href and href.startswith("https://www.myscheme.gov.in/schemes/") and href not in seen_links:
                scheme_list.append({
                    "scheme_name": text if text else "Unnamed Scheme",
                    "url": href
                })
                seen_links.add(href)

    except Exception as e:
        print(f"⚠️ Error loading page {page_num}: {e}")
    
    time.sleep(1)  # Slight delay to avoid hammering server

# Loop through all pages using the visible page number buttons
for page_num in range(1, MAX_PAGES + 1):
    print(f"🔄 Scraping page {page_num}...")

    try:
        extract_scheme_links()

        # Find the <li> for the next page
        pagination_buttons = driver.find_elements(By.CSS_SELECTOR, "ul li.h-8.w-8")

        clicked = False
        for li in pagination_buttons:
            if li.text.strip() == str(page_num + 1):
                driver.execute_script("arguments[0].click();", li)
                clicked = True
                time.sleep(2)
                break

        if not clicked:
            print("✅ Reached last visible page or next page not clickable.")
            break

    except Exception as e:
        print(f"⚠️ Error on page {page_num}: {e}")
        break

# Save results
driver.quit()

with open("myscheme_schemes_all.json", "w", encoding="utf-8") as f:
    json.dump(scheme_list, f, indent=2, ensure_ascii=False)

print(f"\n✅ Done! Extracted {len(scheme_list)} unique schemes.")
