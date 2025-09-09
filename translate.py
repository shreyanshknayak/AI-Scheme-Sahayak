from sarvamai import SarvamAI
from dotenv import load_dotenv
import os
# Load environment variables
load_dotenv()
# Initialize SarvamAI client    

client = SarvamAI(api_subscription_key= os.getenv("SARVAM_API_KEY"))

def chunk_text(text, max_length=2000):
    """Splits text into chunks of at most max_length characters while preserving word boundaries."""
    chunks = []
    while len(text) > max_length:
        split_index = text.rfind(" ", 0, max_length)  # Find the last space within limit
        if split_index == -1:
            split_index = max_length  # No space found, force split at max_length
        chunks.append(text[:split_index].strip())  # Trim spaces before adding
        text = text[split_index:].lstrip()  # Remove leading spaces for the next chunk
    if text:
        chunks.append(text.strip())  # Add the last chunk
    return chunks

source_text_chunks = chunk_text(input("Enter text"), max_length=2000)

print(f"Total Chunks: {len(source_text_chunks)}")
for i, chunk in enumerate(
         source_text_chunks[:3], 1
):  # Show only first 3 chunks for preview
    print(f"\n=== Chunk {i} (Length: {len(chunk)}) ===\n{chunk}")

translated_texts = []
for idx, chunk in enumerate(source_text_chunks):
    response = client.text.translate(
        input=chunk,
        source_language_code="hi-IN",
        target_language_code="sd-IN",
        speaker_gender="Male",
        mode="formal",
        model="sarvam-translate:v1",
        enable_preprocessing=False,
    )

    translated_text = response.translated_text
    print(f"\n=== Translated Chunk {idx + 1} ===\n{translated_text}\n")
    translated_texts.append(translated_text)

# Combine all translated chunks
final_translation = "\n".join(translated_texts)
print("\n=== Final Translated Text in Sindhi ===")
print(final_translation)



