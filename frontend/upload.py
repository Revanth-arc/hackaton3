import streamlit as st
import uuid
import logging
from ocr.image_preprocessing import preprocess_image
from ocr.paddle_reader import extract_text
from ai.extractor import extract_fir_entities, ExtractionError
from database.sqlite import save_fir_draft

logger = logging.getLogger(__name__)

def render_upload_page():
    st.header("Upload Handwritten Complaint")
    
    uploaded_file = st.file_uploader("Choose an image (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Complaint", width=400)
        
        if st.button("Process Complaint"):
            complaint_id = str(uuid.uuid4())
            
            with st.spinner("Step 1: Enhancing Image via OpenCV..."):
                try:
                    # Reset the file pointer since st.image() already consumed the stream
                    uploaded_file.seek(0)
                    image_bytes = uploaded_file.read()
                    enhanced_img = preprocess_image(image_bytes)
                except Exception as e:
                    st.error(f"Image enhancement failed: {e}")
                    return
            
            with st.spinner("Step 2: Extracting Text via PaddleOCR... (This may take a moment)"):
                try:
                    raw_text = extract_text(enhanced_img)
                    st.subheader("Extracted Raw Text")
                    st.text_area("Raw Text", raw_text, height=200)
                except Exception as e:
                    st.error(f"OCR failed: {e}")
                    return
            
            with st.spinner("Step 3: Extracting Entities via local LLM..."):
                try:
                    dto = extract_fir_entities(raw_text)
                    st.success("Extraction Complete!")
                    st.json(dto.model_dump())
                except ExtractionError as e:
                    st.error(str(e))
                    return
                except Exception as e:
                    st.error(f"AI Extraction failed: {e}")
                    return
            
            with st.spinner("Step 4: Saving FIR Draft..."):
                try:
                    fir_id = save_fir_draft(dto, complaint_id)
                    st.success(f"FIR Draft saved successfully! ID: {fir_id}")
                except Exception as e:
                    st.error(f"Failed to save to database: {e}")
