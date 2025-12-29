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

# --- AUTOMATIC ANALYSIS ---
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", width=300)

    with st.spinner("Analyzing waste & pre-disposal steps..."):
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

            # 3. ADVANCED PROMPT (Actionable Steps + Strict Formatting)
            prompt = """
            You are an expert Indian waste management assistant. Analyze the image and provide specific disposal instructions.

            1. **CLASSIFY:** Determine if it goes to Green (Wet), Blue (Dry), or Red (Hazardous) bin.
            2. **ACTION:** Look for liquids, food residue, or volume. 
               - If it's a bottle: Tell user to "Empty liquid, crush it, and separate the cap."
               - If it's a food container: Tell user to "Rinse off food residue."
               - If it's sharp: Tell user to "Wrap it safely in paper."

            **STRICT OUTPUT FORMAT:**
            Line 1: [BIN_COLOR] (Must be exactly "GREEN", "BLUE", or "RED")
            Line 2: [English Instruction] (Short sentence including the action steps like empty/crush/rinse).
            Line 3: ###HINDI_AUDIO###
            Line 4: [Hindi Translation] (Translate the action steps. Must explicitly say "Neela/Hara/Laal Kude-daan").

            Example Output:
            BLUE
            Empty any liquid, crush the bottle, and place it in the Blue Bin.
            ###HINDI_AUDIO###
            Pehle bachi hui liquid fenk dein, bottle ko crush karein, aur phir Neele Kude-daan mein dalein.
            """

            # 4. Generate Response
            response = model.generate_content([prompt, image_parts[0]])
            full_text = response.text.strip()

            # 5. Parse the Output
            # We expect 4 parts, but we split carefully
            if "###HINDI_AUDIO###" in full_text:
                parts = full_text.split("###HINDI_AUDIO###")
                english_part = parts[0].strip().split("\n")
                hindi_text = parts[1].strip()
                
                # Extract Bin Color and Instruction from English Part
                if len(english_part) >= 2:
                    bin_color = english_part[0].strip().upper()
                    english_instruction = " ".join(english_part[1:]).strip()
                else:
                    bin_color = "UNKNOWN"
                    english_instruction = parts[0].strip()
            else:
                bin_color = "UNKNOWN"
                english_instruction = full_text
                hindi_text = "कृपया सही कूड़ेदान का उपयोग करें।"

            # --- DISPLAY RESULTS WITH COLOR ---
            
            # Logic for coloring the box based on the Bin Type
            if "BLUE" in bin_color:
                st.info(f"**🔵 {bin_color} BIN (Dry Waste)**\n\n{english_instruction}")
            elif "GREEN" in bin_color:
                st.success(f"**🟢 {bin_color} BIN (Wet Waste)**\n\n{english_instruction}")
            elif "RED" in bin_color:
                st.error(f"**🔴 {bin_color} BIN (Hazardous)**\n\n{english_instruction}")
            else:
                st.warning(f"**⚠️ Unsure:**\n\n{english_instruction}")
            
            # --- AUDIO SECTION ---
            st.write("🔊 **Hindi Instruction:**")
            
            if hindi_text:
                tts = gTTS(text=hindi_text, lang='hi')
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    tts.save(fp.name)
                    st.audio(fp.name, format="audio/mp3")
            else:
                st.error("Audio generation failed.")

        except Exception as e:
            st.error(f"Error: {e}")
