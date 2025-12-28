import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="SmartBin India", page_icon="♻️")

# --- HIDE STREAMLIT BRANDING ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- SIDEBAR: API KEY SETUP ---
with st.sidebar:
    st.title("⚙️ Configuration")
    api_key = st.text_input("Enter Google API Key", type="password")
    st.info("Get your key from Google AI Studio")

# --- MAIN APP UI ---
st.title("♻️ SmartBin India")
st.subheader("Your AI Assistant for Swachh Bharat 🇮🇳")
st.write("Not sure if it goes in the **Green (Geela)** or **Blue (Sukha)** bin? Upload a photo!")

uploaded_file = st.file_uploader("Take a photo of the waste item", type=["jpg", "png", "jpeg"])

if uploaded_file is not None and api_key:
    image = Image.open(uploaded_file)
    st.image(image, caption="Analyzing waste item...", width=300)

    try:
        genai.configure(api_key=api_key)
        
        # --- THE FIX IS HERE (Using the standard name) ---
        model = genai.GenerativeModel("gemini-1.5-001")

        system_prompt = """
        You are an expert Indian Waste Management Guide. Analyze the image and output purely valid JSON.
        Categories: 
        1. "Green" (Wet/Organic/Kitchen Waste)
        2. "Blue" (Dry/Recyclable/Plastic/Paper)
        3. "Red" (Hazardous/Sanitary/Glass)
        
        Format:
        {
            "bin_type": "Green" or "Blue" or "Red",
            "item_name": "Short Name",
            "instruction": "Action step (e.g. Rinse it, Crush it)",
            "hinglish_tip": "Fun tip in Hinglish",
            "fact": "One short eco-fact"
        }
        """
        
        with st.spinner("🤖 AI is checking Municipal Guidelines..."):
            response = model.generate_content([system_prompt, image])
            text_response = response.text.replace("```json", "").replace("```", "")
            data = json.loads(text_response)
            
            st.divider()
            if data["bin_type"] == "Green":
                st.success(f"✅ GOES IN: **GREEN BIN (WET / GEELA)**")
            elif data["bin_type"] == "Blue":
                st.info(f"♻️ GOES IN: **BLUE BIN (DRY / SUKHA)**")
                st.balloons()
            else:
                st.error(f"⚠️ GOES IN: **RED BIN (HAZARDOUS)**")
            
            st.markdown(f"**Item:** {data['item_name']}")
            st.markdown(f"**Action:** {data['instruction']}")
            st.warning(f"💡 **Tip:** {data['hinglish_tip']}")

    except Exception as e:
        st.error(f"Error: {e}")

elif not api_key:
    st.warning("⚠️ Please enter your API Key in the sidebar to start.")

