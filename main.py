import streamlit as st
import asr
import sounddevice as sd
import numpy as np
import requests

DURATION = 5 # seconds
SAMPLING_RATE = 16000

st.set_page_config(page_title="AI Sahayak", layout="centered")
st.title("📚 AI Sahayak – Government Scheme Assistant")

st.markdown("""
Welcome to **AI Sahayak** – your assistant for discovering and exploring Indian government schemes.

- 📝 Use the **Scheme Screening** page to find eligible schemes based on your inputs.
- 💬 Use the **Scheme Chatbot** page to ask natural questions and get instant answers from Boudhi, your AI assistant.
""")



