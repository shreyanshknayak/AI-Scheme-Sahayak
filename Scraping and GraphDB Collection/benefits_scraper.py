import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Load schemes
with open('myscheme_schemes_all.json', 'r') as f:
    schemes = json.load(f)

# Setup Selenium
'''options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)'''

# Setup headless Chrome
options = Options()
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)

def extract_benefits(driver):
    try:
        # Wait for the Benefits anchor to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="#benefits"]'))
        )
        anchor = driver.find_element(By.CSS_SELECTOR, 'a[href="#benefits"]')
        driver.execute_script("arguments[0].scrollIntoView();", anchor)
        time.sleep(1)

        # Get the next div after the anchor
        next_div = anchor.find_element(By.XPATH, 'following::div[1]')
        benefits = []

        # Check for <li> items
        li_items = next_div.find_elements(By.TAG_NAME, 'li')
        for li in li_items:
            text = li.text.strip()
            if text and text not in benefits:
                benefits.append(text)

        # If no <li>, try <div class="mb-2" ...>
        if not benefits:
            divs = next_div.find_elements(By.XPATH, './/div[@class="mb-2" and @data-slate-node="element"]')
            for div in divs:
                text = div.text.strip()
                if text and text not in benefits:
                    benefits.append(text)

        # If no list/divs, try <table>
        if not benefits:
            tables = next_div.find_elements(By.TAG_NAME, 'table')
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, 'tr')
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    row_text = " | ".join(cell.text.strip() for cell in cells if cell.text.strip())
                    if row_text and row_text not in benefits:
                        benefits.append(row_text)

        return benefits

    except Exception as e:
        print("❌ Error extracting benefits:", e)
        return []

# Iterate through schemes
output = []
for idx, scheme in enumerate(schemes, 1):
    name = scheme['scheme_name']
    url = scheme['url']
    print(f"🔎 [{idx}/{len(schemes)}] {name}")
    print(f"URL: {url}")

    try:
        driver.get(url)
        time.sleep(2)
        benefits = extract_benefits(driver)
    except Exception as e:
        print(f"❌ Failed to process {name}: {e}")
        benefits = []

    output.append({
        "scheme_name": name,
        "url": url,
        "benefits": benefits
    })


# Save results
with open('benefits_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print("✅ Benefits extraction complete. Saved to benefits_results.json")
driver.quit()
