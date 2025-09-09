import streamlit as st
import os
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from dotenv import load_dotenv
# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()
# Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY") # Replace with your Pinecone API key
PINECONE_INDEX_NAME = "govt-schemes"  # Replace with your Pinecone index name

# ----------------------------
# Initialize Pinecone + model
# ----------------------------
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)
model = SentenceTransformer("intfloat/e5-large")

# ----------------------------
# Streamlit App UI
# ----------------------------
st.set_page_config(page_title="Scheme Finder", layout="centered")
st.title("🇮🇳 Government Scheme Recommender")
st.markdown("Find schemes you're eligible for based on your profile.")

# ----------------------------
# Screening Form
# ----------------------------
with st.form("screening_form"):
    age = st.number_input("Your Age", min_value=0, max_value=100)
    gender = st.radio("Gender", ["Male", "Female", "Other"])
    income = st.number_input("Annual Income (₹)", min_value=0)
    occupation = st.text_input("Occupation")
    state = st.text_input("State of Residence")
    education = st.text_input("Highest Education Level")
    submit = st.form_submit_button("🔍 Find Eligible Schemes")

# ----------------------------
# On Submit: Generate Prompt → Embed → Query Pinecone
# ----------------------------
if submit:
    with st.spinner("Searching for matching schemes..."):
        # Create semantic search prompt
        user_prompt = (
            f"I am a {age} year old {gender.lower()} from {state}, earning ₹{income} per year. "
            f"My occupation is {occupation} and I have completed {education} education. "
            "Which government schemes am I eligible for?"
        )

        # Embed user input
        user_embedding = model.encode(user_prompt).tolist()

        # Query Pinecone
        try:
            results = index.query(vector=user_embedding, top_k=5, include_metadata=True)

            if results.matches:
                st.subheader("🎯 Top Matching Schemes")
                for match in results.matches:
                    scheme = match.metadata
                    st.markdown(f"#### {scheme.get('scheme_name', 'Unnamed Scheme')}")
                    if scheme.get("url"):
                        st.markdown(f"[🔗 Learn more]({scheme['url']})")
                    st.markdown("---")
            else:
                st.warning("No matching schemes found. Try adjusting your inputs.")
        except Exception as e:
            st.error(f"Error querying Pinecone: {str(e)}")
