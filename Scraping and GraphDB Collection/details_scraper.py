import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load schemes JSON
with open("myscheme_schemes_all.json", "r") as f:
    schemes = json.load(f)

# Setup headless Chrome
options = Options()
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)

# Extract 'Details' tab content
def extract_details():
    try:
        content_div = WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.CLASS_NAME, "markdown-options"))
        )
        all_elements = content_div.find_elements(By.CSS_SELECTOR, "div.mb-2[data-slate-node='element']")
        final_texts = []

        for el in all_elements:
            # Only get divs that do not contain other similar divs inside
            child_divs = el.find_elements(By.CSS_SELECTOR, "div.mb-2[data-slate-node='element']")
            if not child_divs:
                text = el.text.strip()
                if text:
                    final_texts.append(text)

        return final_texts
    except Exception as e:
        print(f"⚠️ Failed to extract details: {e}")
        return []


# Extract data for all schemes
output_data = []
for i, scheme in enumerate(schemes, 1):
    print(f"🔎 [{i}/{len(schemes)}] {scheme['scheme_name']}")
    try:
        driver.get(scheme['url'])
        time.sleep(2.5)  # Wait for page to render
        details = extract_details()
        output_data.append({
            "scheme_name": scheme['scheme_name'],
            "url": scheme['url'],
            "details": details
        })
    except Exception as e:
        print(f"❌ Error on {scheme['scheme_name']}: {e}")
        output_data.append({
            "scheme_name": scheme['scheme_name'],
            "url": scheme['url'],
            "details": []
        })

# Close driver
driver.quit()

# Save output
with open("myscheme_details_only.json", "w") as f:
    json.dump(output_data, f, indent=2)

print("✅ Saved extracted details to myscheme_details_only.json")
