# T$O Submission : Team Meme Machine (Pitch Video & Documentation)
You can find our pitch video, technical document, and related assets here:

[Google Drive Folder](https://drive.google.com/drive/folders/1BTyux_gmHm96KN4uk7VMd985bEg1-Rsb?usp=sharing)


# 🧠 Boudhi Chatbot – Government Scheme Finder & Screener

Boudhi is a multilingual voice- and text-enabled chatbot built to help users discover and understand government schemes. It supports natural language queries, voice input, and multilingual response output — designed with accessibility and local relevance in mind.

---

## 🔧 Features

- 🎤 **Voice Input (Speech-to-Text)** using a custom ASR engine
- 🧾 **Text Input** with language translation support
- 🔍 **Query Matching** using Pinecone vector search
- 🧠 **LLM-Powered Answers** via Groq API
- 🗣 **Text-to-Speech (TTS)** for voice responses
- 🈯 **Multilingual Input/Output Support** (English + Indian languages)
- 📋 **Screening Logic** for personalized scheme recommendations
- 🕸 **Scheme Scraping & Vector DB** – 1000+ government schemes were scraped and upserted to a Pinecone vector database for semantic search.

---

## 📦 Scraping Process & Dataset Preparation

A dedicated script scrapes data from public portals like [https://www.india.gov.in/](https://www.india.gov.in/) and state scheme directories. For each scheme, we extract:

- ✅ `scheme_name`
- 📝 `details`
- 🧾 `eligibility criteria`
- 💰 `benefits`
- 📎 `application process`
- 📄 `documents required`
- 🔖 `tags/categories`
- 🔗 `official URL`

### JSON Structuring

Each scheme entry is stored in a normalized JSON format:
```json
{
  "scheme_name": "...",
  "details": "...",
  "eligibility": "...",
  "benefits": "...",
  "application_process": "...",
  "documents_required": "...",
  "tags": [...],
  "url": "https://..."
}
````

Over **1000 such entries** were aggregated into a `combined_schemes.json` file.

---

## 🔁 Upserting to Pinecone Vector DB

The `scheme_upsert.py` module handles vector DB ingestion:

1. **Embedding Generation**

   * Uses `intfloat/e5-large` (1024-dim) or `all-MiniLM-L6-v2` (384-dim) from HuggingFace.
   * Each scheme is transformed into a single dense embedding by combining all fields into one paragraph.

2. **Chunking & Size Check**

   * Documents are batched in groups of 50.
   * Text is truncated to avoid Pinecone's 4MB payload limit.

3. **Upsert**

   * If the index is empty, schemes are embedded and upserted using LangChain + Pinecone API.
   * On reruns, ingestion is skipped unless explicitly forced.

```python
from pinecone import Pinecone, ServerlessSpec
...
if index.describe_index_stats().total_vector_count == 0:
    index.upsert(vectors=batch)
```

4. **Metadata**

   * Each vector includes metadata like URL, title, and tags, which can be filtered or viewed on match.

---

## 🤖 Semantic Retrieval with Pinecone + Groq

* User queries are embedded using the same embedding model (e.g., `e5-large`).
* The embedding is passed to Pinecone to retrieve the **most similar scheme vectors** using **cosine similarity**.
* Retrieved results are ranked and passed to a **Groq-hosted LLM** (Mistral/LLama2) for answering the query naturally using context.

```python
retriever = vectorstore.as_retriever()
results = retriever.get_relevant_documents(query)
```

This allows **fuzzy matching** even if the query doesn’t exactly match the scheme name or benefits.

---

## 🗂 File Overview

| File                    | Purpose                                                               |
| ----------------------- | --------------------------------------------------------------------- |
| `main.py`               | Streamlit-based chatbot frontend with text/voice input and TTS output |
| `asr.py`                | Audio capture and transcription logic                                 |
| `Scheme Finder.py`      | Alternate interface version for scheme querying                       |
| `pinecone_utils.py`     | Pinecone vector search utilities for scheme documents                 |
| `scheme_upsert.py`      | Script to upload/index schemes into Pinecone                          |
| `Screening.py`          | Handles scheme eligibility filtering logic                            |
| `scraper/`              | HTML parsing scripts to extract structured data from scheme websites  |
| `combined_schemes.json` | Merged dataset of 1000+ government schemes                            |

---

## 🚀 How It Works

1. **Input Capture**

   * Users type or speak a query in their preferred language.
   * Voice is recorded and transcribed using `asr.py`.
   * Input is translated to English if needed.

2. **Semantic Matching**

   * Query is embedded and passed to `pinecone_utils.py` to find the top relevant schemes using semantic similarity.
   * Matching schemes are forwarded to Groq LLM for summarization and explanation.

3. **Response Output**

   * Answers are shown in the chat window.
   * An optional "🔊 TTS" button reads out the response in the selected language.

4. **Screening**

   * If selected, `Screening.py` asks eligibility questions.
   * Matches are determined via rule-based filters and Pinecone's filtered retrieval.

---

## 🛠 Setup Instructions

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

> Includes `streamlit`, `pinecone-client`, `langchain`, `transformers`, `gtts`, `googletrans`, `dotenv`, etc.

2. **Configure `.env`**

```
GROQ_API_KEY=your_groq_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_env
```

3. **Run the app**

```bash
streamlit run main.py
```

---

## 🌐 Language Support

* ✍️ Input: Text or speech in English, Hindi, Tamil, etc.
* 🧠 Processing: Translated to English for understanding
* 🗣 Output: Text and optional voice (TTS) in original language

---

## 🧠 Roadmap & Enhancements

* Build Neo4j Knowledge Graph for richer scheme interlinking
* Incorporate grievance redressal features (CPGRAMS integration)
* Skeumorphic UI to help digitally illiterate users
* Offline/low-bandwidth mode for rural areas
* Regional dialect embeddings for precise local matching
* In-app scheme application workflow

---

## 🧑‍💻 Contributors

* **Tanav Kolar**
* **Shreyansh Kumar Nayak**

---
## Declaration

AI-assistance was used in generating some of the code found in this repository.



