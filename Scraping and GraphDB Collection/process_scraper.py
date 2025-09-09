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

def extract_application_process(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="#application-process"]'))
        )
        anchor = driver.find_element(By.CSS_SELECTOR, 'a[href="#application-process"]')
        driver.execute_script("arguments[0].scrollIntoView();", anchor)
        time.sleep(1)

        # Get the next div following the anchor
        next_div = anchor.find_element(By.XPATH, 'following::div[1]')

        steps = []

        # First, extract <li> steps
        li_items = next_div.find_elements(By.TAG_NAME, 'li')
        for li in li_items:
            text = li.text.strip()
            if text and text not in steps:
                steps.append(text)

        # If no <li>, fallback to <div class="mb-2" ...>
        if not steps:
            divs = next_div.find_elements(By.XPATH, './/div[@class="mb-2" and @data-slate-node="element"]')
            for div in divs:
                text = div.text.strip()
                if text and text not in steps:
                    steps.append(text)

        return steps

    except Exception as e:
        print("❌ Error extracting application process:", e)
        return []

# Loop through all schemes
output = []
for idx, scheme in enumerate(schemes, 1):
    name = scheme['scheme_name']
    url = scheme['url']
    print(f"🔎 [{idx}/{len(schemes)}] {name}")
    print(f"URL: {url}")

    try:
        driver.get(url)
        time.sleep(2)
        application_steps = extract_application_process(driver)
    except Exception as e:
        print(f"❌ Failed to process {name}: {e}")
        application_steps = []

    output.append({
        "scheme_name": name,
        "url": url,
        "application_process": application_steps
    })


# Save results
with open('application_process_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print("✅ Extraction complete. Saved to application_process_results.json")
driver.quit()
