import streamlit as st
from pinecone_utils import query_index
from groq import Groq
import os
import io
import requests
from dotenv import load_dotenv
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Setup Groq client
groq_client = Groq(api_key=groq_api_key)

# Voice recording config
DURATION = 10  # seconds
SAMPLING_RATE = 16000

st.set_page_config(page_title="Boudhi Chatbot", layout="centered")
st.title("💬 Ask Boudhi – Your Scheme Assistant")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "state" not in st.session_state:
    st.session_state.state = {}

# Store empty transcript string
transcript = ""

# Record and transcribe audio using Groq Whisper API
if st.button("🎤 Start Recording"):
    st.write("Recording... Speak now!")
    audio = sd.rec(int(DURATION * SAMPLING_RATE), samplerate=SAMPLING_RATE, channels=1, dtype='float32')
    sd.wait()
    st.write("Transcribing...")

    # Convert float32 audio to int16
    audio_int16 = np.int16(audio.flatten() * 32767)

    # Write WAV to in-memory buffer
    buffer = io.BytesIO()
    write(buffer, SAMPLING_RATE, audio_int16)
    buffer.seek(0)

    # Transcribe using Groq Whisper
    try:
        transcription = groq_client.audio.transcriptions.create(
            file=("audio.wav", buffer.read()),
            model="whisper-large-v3-turbo",
            response_format="verbose_json",
        )
        transcript = transcription.text
        st.success("Transcription:")
        st.write(transcript)
    except Exception as e:
        st.error(f"Transcription failed: {e}")

# Get user input from voice or chat
query = st.chat_input("Ask about schemes, benefits, eligibility...", key="user_input")
user_input = transcript if transcript else query

# Handle user query
if user_input:
    # Retrieve relevant schemes
    search_results = query_index(user_input)
    retrieved_info = "\n\n".join(
        f"Scheme: {m.metadata.get('scheme_name', '')}\nDetails: {m.metadata}" for m in search_results.matches
    )

    # Create chat prompt
    system_prompt = (
        "You are a helpful assistant for Indian government schemes. "
        "Use the retrieved scheme data to answer questions accurately and clearly."
    )
    messages = [{"role": "system", "content": system_prompt}]
    messages += st.session_state.chat_history
    messages.append({
        "role": "user",
        "content": f"{user_input}\n\nContext:\n{retrieved_info}"
    })

    # Save user query
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Call Groq Chat Completion
    with st.spinner("Boudhi is thinking..."):
        try:
            response = groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages,
                temperature=0.7
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"Error from Groq API: {e}"

        # Save assistant reply
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
