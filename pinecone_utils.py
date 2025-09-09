# pinecone_utils.py
import os
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
# Load environment variables
load_dotenv()
# Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "govt-schemes"
EMBEDDING_MODEL = "intfloat/e5-large"

model = SentenceTransformer(EMBEDDING_MODEL)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

def embed_text(text):
    return model.encode(text).tolist()

def query_index(text, top_k=5):
    embedding = embed_text(text)
    return index.query(vector=embedding, top_k=top_k, include_metadata=True)
