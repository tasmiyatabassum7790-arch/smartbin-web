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

    with st.spinner("Analyzing waste details..."):
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

            # 3. SMART PROMPT (Detailed + Audio)
            prompt = """
            You are an expert Indian waste management assistant. 
            Analyze the image in detail. Identify exactly what the item is (e.g., "Plastic Ghee Bottle with residue", "Cardboard box", "Banana peel").

            1. **CLASSIFY:** Determine if it goes to Green (Wet), Blue (Dry), or Red (Hazardous) bin.
            2. **SPECIFIC INSTRUCTIONS:** Look closely at the image.
               - If it has food/oil residue (like ghee, jam, ketchup), tell the user to **wash and dry it** properly.
               - If it has a cap/lid, tell them to separate it if needed.
               - If it is crushed or broken, mention safety.

            **STRICT OUTPUT FORMAT:**
            Line 1: [BIN_COLOR] (Must be exactly "GREEN", "BLUE", or "RED")
            Line 2: [English Instruction] (A natural, helpful explanation of what the item is and exactly how to clean/dispose of it).
            Line 3: ###HINDI_AUDIO###
            Line 4: [Hindi Translation] (Translate the specific instruction to simple spoken Hindi. Explicitly mention "Neela/Hara/Laal Kude-daan").

            """

            # 4. Generate Response
            response = model.generate_content([prompt, image_parts[0]])
            full_text = response.text.strip()

            # 5. Parse the Output
            if "###HINDI_AUDIO###" in full_text:
                parts = full_text.split("###HINDI_AUDIO###")
                english_part = parts[0].strip().split("\n")
                hindi_text = parts[1].strip()
                
                # Extract Bin Color and Instruction
                if len(english_part) >= 2:
                    bin_color = english_part[0].strip().upper()
                    # Join the rest of the lines as the instruction
                    english_instruction = " ".join(english_part[1:]).strip()
                else:
                    bin_color = "UNKNOWN"
                    english_instruction = parts[0].strip()
            else:
                bin_color = "UNKNOWN"
                english_instruction = full_text
                hindi_text = "कृपया इसे साफ करके सही कूड़ेदान में डालें।"

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
            st.write("🔊 **Hindi Instruction:**")
            
            if hindi_text:
                tts = gTTS(text=hindi_text, lang='hi')
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    tts.save(fp.name)
                    st.audio(fp.name, format="audio/mp3")

        except Exception as e:
            st.error(f"Error: {e}")
