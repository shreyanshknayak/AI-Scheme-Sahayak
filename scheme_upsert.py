import json
import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from dotenv import load_dotenv
# Load environment variables
load_dotenv()
# --- Configuration ---
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "govt-schemes"
REGION = "us-east-1"
CLOUD = "aws"
DIMENSION = 1024  # for intfloat/e5-large
EMBEDDING_MODEL_NAME = "intfloat/e5-large"
SCHEMES_FILE = "combined_schemes.json"
BATCH_SIZE = 100

# --- Load data ---
with open(SCHEMES_FILE, "r", encoding="utf-8") as f:
    schemes = json.load(f)

# --- Load embedding model ---
print("Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# --- Connect to Pinecone ---
print("Connecting to Pinecone...")
pc = Pinecone(api_key=PINECONE_API_KEY)

# --- Create index if it doesn't exist ---
if INDEX_NAME not in pc.list_indexes().names():
    print(f"Creating index: {INDEX_NAME}")
    pc.create_index(
        name=INDEX_NAME,
        dimension=DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(
            cloud=CLOUD,
            region=REGION
        )
    )

index = pc.Index(INDEX_NAME)

# --- Prepare data for upsert ---
print("Preparing embeddings and metadata...")
to_upsert = []

for i, scheme in tqdm(enumerate(schemes), total=len(schemes)):
    scheme_id = f"scheme-{i}"

    # Compose text for semantic embedding
    text = (
        f"{scheme.get('scheme_name', '')}. "
        f"Eligibility: {scheme.get('eligibility', '')}. "
        f"Benefits: {scheme.get('benefits', '')}. "
        f"Details: {scheme.get('details', '')}. "
        f"Application Process: {scheme.get('application_process', '')}. "
        f"Documents Required: {scheme.get('documents_required', '')}. "
        f"Tags: {', '.join(scheme.get('tags', []))}"
    )

    # Compute embedding
    embedding = model.encode(text)

    # Metadata for retrieval
    metadata = {
        "scheme_name": scheme.get("scheme_name", ""),
        "url": scheme.get("url", ""),
        "details": scheme.get("details", ""),
        "eligibility": scheme.get("eligibility", ""),
        "benefits": scheme.get("benefits", ""),
        "application_process": scheme.get("application_process", ""),
        "documents_required": scheme.get("documents_required", ""),
        "tags": scheme.get("tags", [])
    }

    to_upsert.append((scheme_id, embedding.tolist(), metadata))

# --- Upload to Pinecone in batches ---
print("Uploading to Pinecone...")
for i in range(0, len(to_upsert), BATCH_SIZE):
    batch = to_upsert[i:i + BATCH_SIZE]
    index.upsert(vectors=batch)

print(f"✅ Upsert complete. {len(to_upsert)} schemes indexed.")
