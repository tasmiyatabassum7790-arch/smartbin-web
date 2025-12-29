import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import tempfile
import os

# --- PAGE SETUP ---
st.set_page_config(page_title="Smart Waste Sorter", page_icon="♻️")
st.header("♻️ Smart Waste Sorter")

# --- API KEY SETUP ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing API Key. Please add it to your Streamlit secrets.")

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader("Upload an image of waste...", type=["jpg", "jpeg", "png"])

# --- AUTOMATIC ANALYSIS (No Button) ---
if uploaded_file is not None:
    # Display the image small and centered
    st.image(uploaded_file, caption="Uploaded Image", width=300)

    with st.spinner("Identifying correct bin..."):
        try:
            # 1. Setup Model
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # 2. Process Image
            image_bytes = uploaded_file.getvalue()
            image_parts = [
                {
                    "mime_type": uploaded_file.type,
                    "data": image_bytes
                }
            ]

            # 3. STRICT SHORT PROMPT
            prompt = """
            You are an expert waste sorter. Analyze the image and determine if it goes to the Green, Blue, or Red bin in India.
            
            Output strictly in this format:
            1. **BIN: [INSERT BIN COLOR HERE]** 2. [One very short sentence on how to dispose it].
            3. "###HINDI_AUDIO###"
            4. [Hindi translation of the short sentence. You MUST explicitly say "Neela Kude-daan", "Hara Kude-daan", or "Laal Kude-daan"].

            Do NOT provide descriptions. Do NOT provide definitions. Keep it extremely short.
            """

            # 4. Generate Response
            response = model.generate_content([prompt, image_parts[0]])
            full_text = response.text

            # 5. Separate English & Hindi
            if "###HINDI_AUDIO###" in full_text:
                parts = full_text.split("###HINDI_AUDIO###")
                english_text = parts[0].strip()
                hindi_text = parts[1].strip()
            else:
                english_text = full_text
                hindi_text = "कृपया सही कूड़ेदान का उपयोग करें।"

            # --- DISPLAY RESULTS ---
            
            # Show English Text (Result Only)
            st.success(english_text)
            
            # Show Audio Player for Hindi
            st.write("🔊 **Hindi Instruction:**")
            
            # Create audio file in memory
            tts = gTTS(text=hindi_text, lang='hi')
            
            # Save to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                tts.save(fp.name)
                st.audio(fp.name, format="audio/mp3")

        except Exception as e:
            st.error(f"Error: {e}")
