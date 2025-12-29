import streamlit as st
import requests
import time
from io import BytesIO

# Constants
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="ModaMood", page_icon="👗", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if 'captions' not in st.session_state:
    st.session_state['captions'] = []
if 'aesthetic_summary' not in st.session_state:
    st.session_state['aesthetic_summary'] = None
if 'current_image' not in st.session_state:
    st.session_state['current_image'] = None
if 'analysis_done' not in st.session_state:
    st.session_state['analysis_done'] = False

# Sidebar
with st.sidebar:
    st.title("👗 ModaMood")
    st.write("**AI Co-Creative Fashion Generator**")
    st.info("Upload your moodboard, generate a cohesive aesthetic, and refine your new look.")
    st.markdown("---")
    
    # Gender/Style Selector
    target_audience = st.radio(
        "2. Target Audience / Style",
        ["Neutral/Unisex", "Womenswear", "Menswear"],
        index=0
    )
    
    # File Uploader in Sidebar
    uploaded_files = st.file_uploader("3. Upload Moodboard (3-6 images)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("🔍 Analyze Images", type="primary"):
            with st.spinner("Analyzing style DNA..."):
                files = [('files', (file.name, file, file.type)) for file in uploaded_files]
                try:
                    # Reset file pointers
                    for file in uploaded_files:
                        file.seek(0)
                    
                    caption_res = requests.post(f"{BACKEND_URL}/caption_images", files=files)
                    
                    if caption_res.status_code == 200:
                        data = caption_res.json()
                        st.session_state['captions'] = data.get("captions", [])
                        st.session_state['analysis_done'] = True
                        st.session_state['aesthetic_summary'] = None # Reset summary
                        st.session_state['current_image'] = None     # Reset image
                        st.session_state['target_gender'] = target_audience # Store gender
                        st.success("Analysis Complete! Review captions below.")
                    else:
                        st.error(f"Captioning Failed: {caption_res.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

# Main Content Area
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("🧬 Aesthetic DNA")
    
    if st.session_state['analysis_done'] and st.session_state['captions']:
        st.write("Review the detected styles. Edit if necessary to improve accuracy.")
        
        # Caption Editor
        edited_captions = []
        for i, cap in enumerate(st.session_state['captions']):
            if "Analysis Failed" in cap or "Manual Input" in cap:
                st.warning(f"⚠️ Image {i+1}: AI Analysis Server Overloaded. Please describe the item manually below (e.g., 'Blue denim jacket').")
            
            edited_cap = st.text_area(f"Image {i+1}", value=cap, height=70, key=f"cap_{i}")
            edited_captions.append(edited_cap)
            
        st.session_state['captions'] = edited_captions # Update state
        
        if st.button("✨ Generate Outfit Concept"):
            with st.spinner("Synthesizing and Dreaming..."):
                try:
                    # 2. Summarization
                    payload = {
                        "captions": st.session_state['captions'],
                        "gender": st.session_state.get('target_gender', "Neutral/Unisex")
                    }
                    summary_res = requests.post(f"{BACKEND_URL}/summarize_aesthetic", json=payload)
                    
                    if summary_res.status_code == 200:
                        summary_data = summary_res.json()
                        st.session_state['aesthetic_summary'] = summary_data.get("summary", "")
                        
                        # 3. Initial Generation with gender
                        gen_res = requests.post(f"{BACKEND_URL}/generate_outfit", json={
                            "aesthetic_summary": st.session_state['aesthetic_summary'],
                            "gender": st.session_state.get('target_gender', "Neutral/Unisex")
                        })
                        
                        if gen_res.status_code == 200:
                            import base64
                            response_data = gen_res.json()
                             # Handle new contract
                            image_bytes = base64.b64decode(response_data.get("image_base64"))
                            st.session_state['current_image'] = image_bytes
                            # Update summary if refined (or initial)
                            st.session_state['aesthetic_summary'] = response_data.get("aesthetic_summary")
                            st.rerun()
                        else:
                            st.error(f"Generation Failed: {gen_res.text}")
                    else:
                         st.error(f"Summarization Failed: {summary_res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    elif st.session_state['aesthetic_summary']: # Re-display summary if already generated
        st.success(st.session_state['aesthetic_summary'])
        
    else:
        st.info("Upload images and click 'Analyze' to start.")

with col2:
    st.subheader("✨ Generated Concept")
    
    if st.session_state['aesthetic_summary']:
         st.markdown(f"**Style Summary:** {st.session_state['aesthetic_summary']}")
         
    if st.session_state['current_image']:
        st.image(st.session_state['current_image'], use_container_width=True, caption="AI Generated Outfit")
        
        st.markdown("### 🎨 Refine Look")
        refinement_text = st.text_input("Refinement Command", placeholder="e.g. 'change pants to black', 'add a hat'")
        
        if st.button("Regenerate"):
            if refinement_text:
                with st.spinner("Applying changes..."):
                    try:
                        payload = {
                            "aesthetic_summary": st.session_state['aesthetic_summary'],
                            "gender": st.session_state.get('target_gender', "Neutral/Unisex"),
                            "refinement_command": refinement_text
                        }
                        gen_res = requests.post(f"{BACKEND_URL}/generate_outfit", json=payload)
                        
                        if gen_res.status_code == 200:
                            import base64
                            response_data = gen_res.json()
                            image_bytes = base64.b64decode(response_data.get("image_base64"))
                            st.session_state['current_image'] = image_bytes
                            st.session_state['aesthetic_summary'] = response_data.get("aesthetic_summary")
                            st.success("Updated!")
                            st.rerun()
                        else:
                            st.error(f"Refinement Failed: {gen_res.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Enter a command first.")
    else:
        st.write("Your generated outfit will appear here.")

st.markdown("---")
st.caption("ModaMood v1.1 - Co-Creative Edition")
