import json
import re
from neo4j import GraphDatabase

# --- Neo4j Connection ---
driver = GraphDatabase.driver(
    "neo4j+s://b29c136e.databases.neo4j.io",
    auth=("neo4j", "X6B8PsKnPs7OjnpyuIFHuyKsWga9WF7BcfvmWDQ7BiM")  # Update this before running
)

# --- Structured Eligibility Extraction ---
def extract_structured_eligibility(eligibility_text):
    structured = []

    if isinstance(eligibility_text, list):
        eligibility_text = " ".join(eligibility_text)
    if not isinstance(eligibility_text, str):
        return structured

    if re.search(r'\bSC\b', eligibility_text): structured.append({'name': 'SC', 'type': 'category'})
    if re.search(r'\bST\b', eligibility_text): structured.append({'name': 'ST', 'type': 'category'})
    if 'OBC' in eligibility_text: structured.append({'name': 'OBC', 'type': 'category'})
    if 'women' in eligibility_text or 'female' in eligibility_text: structured.append({'name': 'female', 'type': 'gender'})
    if 'widow' in eligibility_text: structured.append({'name': 'widow', 'type': 'category'})
    if 'girl child' in eligibility_text: structured.append({'name': 'girl child', 'type': 'category'})

    match_income = re.search(r'income.*?(below|less than)? ?₹?[\d,]+', eligibility_text)
    if match_income:
        structured.append({'name': match_income.group(0), 'type': 'economic'})

    states_and_ut = [
        # States
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
        "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
        "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
        "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
        "Uttar Pradesh", "Uttarakhand", "West Bengal",

        # Union Territories
        "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
        "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
    ]

    for state in states_and_ut:
        if state.lower() in eligibility_text.lower():
            structured.append({'name': state, 'type': 'location'})

    return structured

# --- Document Extraction ---
def extract_documents(text):
    if isinstance(text, list):
        return [doc.strip() for doc in text if isinstance(doc, str) and doc.strip()]
    elif isinstance(text, str):
        return [doc.strip() for doc in text.split(',') if doc.strip()]
    return []

# --- Neo4j Insertion ---
def insert_scheme(tx, scheme):
    raw_eligibility = scheme.get("eligibility", "")
    if isinstance(raw_eligibility, list):
        eligibility_text = " ".join(raw_eligibility)
    elif isinstance(raw_eligibility, str):
        eligibility_text = raw_eligibility
    else:
        eligibility_text = ""

    documents = extract_documents(scheme.get("documents_required", ""))
    structured_eligibility = extract_structured_eligibility(eligibility_text)

    tx.run("""
    MERGE (s:Scheme {name: $name})
    SET s.url = $url,
        s.details = $details,
        s.application_process = $application_process,
        s.eligibility_text = $eligibility_text,
        s.benefits = $benefits

    WITH s
    UNWIND $structured_eligibility AS cond
        MERGE (e:EligibilityCondition {name: cond.name})
        SET e.type = cond.type
        MERGE (s)-[:HAS_ELIGIBILITY]->(e)

    WITH s
    UNWIND $documents AS doc
        MERGE (d:Document {name: doc})
        MERGE (s)-[:REQUIRES_DOCUMENT]->(d)

    WITH s
    UNWIND $tags AS tag
        MERGE (t:Tag {label: tag})
        MERGE (s)-[:HAS_TAG]->(t)
    """,
    name=scheme.get("scheme_name", ""),
    url=scheme.get("url", ""),
    details=scheme.get("details", ""),
    application_process=scheme.get("application_process", ""),
    eligibility_text=eligibility_text,
    benefits=scheme.get("benefits", ""),
    structured_eligibility=structured_eligibility,
    documents=documents,
    tags=scheme.get("tags", []))

# --- Load & Ingest All Schemes ---
def ingest_all_schemes(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        all_schemes = json.load(f)

    success_count = 0
    fail_count = 0

    with driver.session() as session:
        for i, scheme in enumerate(all_schemes, start=1):
            name = scheme.get("scheme_name", f"Scheme #{i}")
            print(f"🔄 Inserting scheme {i}/{len(all_schemes)}: {name}...")
            try:
                session.execute_write(insert_scheme, scheme)
                print(f"✅ Successfully inserted: {name}")
                success_count += 1
            except Exception as e:
                print(f"❌ Error inserting '{name}': {e}")
                fail_count += 1

    print("\n📊 Ingestion Summary:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Failed: {fail_count}")
    print("🚀 All done.")

# --- Run It ---
if __name__ == "__main__":
    ingest_all_schemes("combined_schemes.json")
