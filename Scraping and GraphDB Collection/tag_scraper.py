import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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


def extract_tags(driver):
    try:
        # Wait until any tag container is loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[title][class*="border"]'))
        )
        time.sleep(1)

        # Find all tag/category divs with a title attribute
        tag_elements = driver.find_elements(By.CSS_SELECTOR, 'div[title][class*="border"]')

        tags = []
        for tag in tag_elements:
            title = tag.get_attribute("title").strip()
            if title and title not in tags:
                tags.append(title)
        return tags

    except Exception as e:
        print("❌ Error extracting tags:", e)
        return []

# Main loop
output = []
for idx, scheme in enumerate(schemes, 1):
    name = scheme['scheme_name']
    url = scheme['url']
    print(f"🔎 [{idx}/{len(schemes)}] {name}")
    print(f"URL: {url}")

    try:
        driver.get(url)
        time.sleep(2)
        tags = extract_tags(driver)
    except Exception as e:
        print(f"❌ Failed to process {name}: {e}")
        tags = []

    output.append({
        "scheme_name": name,
        "url": url,
        "tags": tags
    })


# Save to file
with open('tags_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print("✅ Tags extraction complete. Saved to tags_results.json")
driver.quit()
