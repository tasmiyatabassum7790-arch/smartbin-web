import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import tempfile

# --- PAGE SETUP ---
st.set_page_config(page_title="Smart Waste Sorter", page_icon="♻️")
st.header("♻️ Smart Waste Sorter & Recycler")

# --- API KEY SETUP ---
# You can put your key here for testing, or use st.secrets for GitHub deployment
# api_key = "YOUR_ACTUAL_API_KEY_HERE" 
# genai.configure(api_key=api_key)

# Ideally, grab from secrets (Recommended for GitHub)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing API Key. Please add it to your Streamlit secrets.")

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader("Upload an image of waste...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the image
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    if st.button("Analyze Waste"):
        with st.spinner("Analyzing... (Thinking in English & Hindi)"):
            try:
                # 1. Setup Model (Gemini 2.5 Flash)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # 2. Convert uploaded file to bytes for Gemini
                image_bytes = uploaded_file.getvalue()
                image_parts = [
                    {
                        "mime_type": uploaded_file.type,
                        "data": image_bytes
                    }
                ]

                # 3. Prompt Strategy
                prompt = """
                Analyze this waste item.
                1. First, provide a clear description and recycling instructions in English.
                2. Then, print the separator string "###HINDI_AUDIO###".
                3. Finally, provide the same instructions translated into simple, spoken Hindi.
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
                    hindi_text = "माफ़ कीजिये, मैं हिंदी अनुवाद नहीं कर सका।"

                # --- DISPLAY RESULTS ---
                
                # Show English Text
                st.subheader("English Instructions")
                st.write(english_text)
                
                st.markdown("---") # Divider line

                # Show Audio Player for Hindi
                st.subheader("🔊 Hindi Audio Instruction")
                
                # Create audio file in memory
                tts = gTTS(text=hindi_text, lang='hi')
                
                # Save to a temporary file so Streamlit can read it
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    tts.save(fp.name)
                    st.audio(fp.name, format="audio/mp3")

            except Exception as e:
                st.error(f"An error occurred: {e}")
