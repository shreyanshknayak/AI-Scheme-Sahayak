import os
import json
from collections import defaultdict

# Use the current script directory
input_folder = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(input_folder, "combined_schemes.json")
tags_file = os.path.join(input_folder, "tags_results.json")

# Initialize the combined data structure
combined_data = defaultdict(lambda: {
    "scheme_name": None,
    "url": None,
    "details": None,
    "eligibility": None,
    "benefits": None,
    "application_process": None,
    "documents_required": None,
    "tags": []
})

# Step 1: Load and merge all individual scheme files
for filename in os.listdir(input_folder):
    if filename.endswith(".json") and filename not in ["combined_schemes.json", "tags_results.json"]:
        file_path = os.path.join(input_folder, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                entry = json.load(f)
                entries = entry if isinstance(entry, list) else [entry]
                for item in entries:
                    name = item.get("scheme_name")
                    url = item.get("url")
                    if not name:
                        continue
                    scheme = combined_data[name]
                    scheme["scheme_name"] = name
                    scheme["url"] = url or scheme["url"]
                    for key in ["details", "eligibility", "benefits", "application_process", "documents_required"]:
                        if key in item:
                            scheme[key] = item[key]
            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")

# Step 2: Add tag information from tags_results.json
if os.path.exists(tags_file):
    with open(tags_file, 'r', encoding='utf-8') as f:
        try:
            tags_data = json.load(f)
            for tag_entry in tags_data:
                name = tag_entry.get("scheme_name")
                tags = tag_entry.get("tags", [])
                if name in combined_data:
                    combined_data[name]["tags"] = tags
        except Exception as e:
            print(f"❌ Error reading tags_results.json: {e}")
else:
    print("⚠️ tags_results.json not found, skipping tag merging.")

# Convert to list format
final_data = list(combined_data.values())

# Step 3: Save the final combined data
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(final_data, f, indent=2, ensure_ascii=False)

print(f"\n✅ Successfully combined {len(final_data)} schemes with tags into: {output_file}")
