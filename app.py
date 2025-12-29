import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import tempfile
import os

# --- PAGE SETUP ---
st.set_page_config(page_title="Smart Waste Sorter", page_icon="♻️")
st.header("♻️ Smart Waste Sorter")

# --- MANUAL API KEY ENTRY ---
st.markdown("### 🔑 Enter API Key")
api_key = st.text_input("Paste your Google Gemini API Key here:", type="password")

if not api_key:
    st.warning("⚠️ Please enter an API Key to use the app.")
    st.stop()  # Stop the app here until key is entered

# Configure the API with the entered key
try:
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Invalid API Key: {e}")

# --- LANGUAGE SELECTOR ---
languages = {
    "Hindi (हिंदी)": "hi",
    "Kannada (ಕನ್ನಡ)": "kn",
    "English": "en",
    "Telugu (తెలుగు)": "te",
    "Tamil (தமிழ்)": "ta",
    "Malayalam (മലയാളം)": "ml"
}

selected_lang_name = st.selectbox("Select Audio Language / ಭಾಷೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಿ", list(languages.keys()))
selected_lang_code = languages[selected_lang_name]

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader("Upload an image of waste...", type=["jpg", "jpeg", "png"])

# --- AUTOMATIC ANALYSIS ---
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", width=300)

    with st.spinner(f"Analyzing waste & generating {selected_lang_name} audio..."):
        try:
            # 1. Setup Model (Using a reliable model version)
            model = genai.GenerativeModel('gemini-2.0-flash-exp') 
            
            # 2. Process Image
            image_bytes = uploaded_file.getvalue()
            image_parts = [
                {
                    "mime_type": uploaded_file.type,
                    "data": image_bytes
                }
            ]

            # 3. DYNAMIC PROMPT
            prompt = f"""
            You are an expert Indian waste management assistant. 
            Analyze the image in detail. Identify exactly what the item is.

            1. **CLASSIFY:** Determine if it goes to Green (Wet), Blue (Dry), or Red (Hazardous) bin.
            2. **SPECIFIC INSTRUCTIONS:** Look for food/oil residue, caps, or broken parts. Tell the user how to clean or separate it.

            **STRICT OUTPUT FORMAT:**
            Line 1: [BIN_COLOR] (Must be exactly "GREEN", "BLUE", or "RED")
            Line 2: [English Instruction] (A natural, helpful explanation in English).
            Line 3: ###AUDIO_TEXT###
            Line 4: [{selected_lang_name} Translation] (Translate the instruction to simple spoken {selected_lang_name}. Explicitly mention the Bin Color in {selected_lang_name}).
            """

            # 4. Generate Response
            response = model.generate_content([prompt, image_parts[0]])
            full_text = response.text.strip()

            # 5. Parse the Output
            if "###AUDIO_TEXT###" in full_text:
                parts = full_text.split("###AUDIO_TEXT###")
                english_part = parts[0].strip().split("\n")
                translated_text = parts[1].strip()
                
                # Extract Bin Color and Instruction
                if len(english_part) >= 2:
                    bin_color = english_part[0].strip().upper()
                    english_instruction = " ".join(english_part[1:]).strip()
                else:
                    bin_color = "UNKNOWN"
                    english_instruction = parts[0].strip()
            else:
                bin_color = "UNKNOWN"
                english_instruction = full_text
                translated_text = "Translation failed."

            # --- DISPLAY RESULTS ---
            
            # Logic for coloring the box
            if "BLUE" in bin_color:
                st.info(f"**🔵 {bin_color} BIN (Dry Waste)**\n\n{english_instruction}")
            elif "GREEN" in bin_color:
                st.success(f"**🟢 {bin_color} BIN (Wet Waste)**\n\n{english_instruction}")
            elif "RED" in bin_color:
                st.error(f"**🔴 {bin_color} BIN (Hazardous)**\n\n{english_instruction}")
            else:
                st.warning(f"**⚠️ Analysis:**\n\n{english_instruction}")
            
            # --- AUDIO SECTION ---
            st.write(f"🔊 **{selected_lang_name} Instruction:**")
            st.write(f"_{translated_text}_")
            
            if translated_text:
                try:
                    tts = gTTS(text=translated_text, lang=selected_lang_code)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                        tts.save(fp.name)
                        st.audio(fp.name, format="audio/mp3")
                except Exception as e:
                    st.error(f"Audio error: {e}")

        except Exception as e:
            st.error(f"Error: {e}")
