import hashlib
import logging
import time
import uuid

import streamlit as st

from ai.extractor import ExtractionError, extract_fir_entities
from database.repository import get_complaint_by_hash
from database.sqlite import save_fir_draft
from ingestion.file_detector import detect_file_type
from ingestion.pdf_handler import process_pdf
from ocr.image_preprocessing import preprocess_image
from ocr.paddle_reader import extract_text

logger = logging.getLogger(__name__)


def render_upload_page():
    st.header("Upload Handwritten or Digital Complaint")

    uploaded_file = st.file_uploader(
        "Choose a file (PDF, JPG, PNG)", type=["pdf", "jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()

        # 1. Detect file type
        file_type = detect_file_type(file_bytes)
        is_pdf = "pdf" in file_type.lower()

        st.subheader("File Information")
        c1, c2, c3 = st.columns(3)
        c1.write(f"**Filename:** {uploaded_file.name}")
        c2.write(f"**Type:** {file_type}")
        c3.write(f"**Size:** {len(file_bytes) / 1024:.2f} KB")

        # 2. Preview
        if not is_pdf:
            st.image(file_bytes, caption="Uploaded Complaint", width=400)
        else:
            st.info("PDF Preview: To see the full document, use your local PDF viewer.")

        # 3. Cache Checking
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        existing = get_complaint_by_hash(file_hash)

        if existing:
            st.success("This file has already been processed! Displaying cached results.")
            st.json(existing)
            st.info(f"You can view this in History under ID: {existing.get('complaint_id')}")
            return

        if st.button("Process Complaint"):
            complaint_id = str(uuid.uuid4())

            metadata = {
                "filename": uploaded_file.name,
                "file_type": file_type,
                "page_count": 1,
                "file_hash": file_hash,
                "processing_method": "OCR",
                "ocr_required": True,
            }

            raw_text = ""

            # 4. Extraction
            if is_pdf:
                progress_bar = st.progress(0, text="Reading PDF...")

                def pdf_progress(current, total, status):
                    msg = f"Reading PDF... Page {current} of {total} ({status})"
                    progress_bar.progress(current / total, text=msg)

                with st.spinner("Extracting text from PDF..."):
                    try:
                        pdf_result = process_pdf(file_bytes, pdf_progress)
                        raw_text = pdf_result["text"]
                        metadata["page_count"] = pdf_result["page_count"]
                        metadata["processing_method"] = pdf_result["processing_method"]
                        metadata["ocr_required"] = pdf_result["ocr_required"]
                        progress_bar.empty()
                    except Exception as e:
                        st.error(f"PDF processing failed: {e}")
                        return
            else:
                with st.spinner("Step 1: Enhancing Image via OpenCV..."):
                    try:
                        enhanced_img = preprocess_image(file_bytes)
                    except Exception as e:
                        st.error(f"Image enhancement failed: {e}")
                        return

                with st.spinner(
                    "Step 2: Extracting Text via PaddleOCR... (This may take a moment)"
                ):
                    try:
                        raw_text = extract_text(enhanced_img)
                    except Exception as e:
                        st.error(f"OCR failed: {e}")
                        return

            # Show extracted text
            with st.expander("View Extracted Raw Text"):
                st.text_area("Raw Text", raw_text, height=200)

            # 5. Entity Extraction (LLM)
            with st.spinner("Step 3: Extracting Entities via local LLM..."):
                try:
                    start_time = time.time()
                    dto = extract_fir_entities(raw_text)
                    llm_time = time.time() - start_time
                    st.success(f"Extraction Complete in {llm_time:.2f}s!")
                    st.json(dto.model_dump())
                except ExtractionError as e:
                    st.error(str(e))
                    return
                except Exception as e:
                    st.error(f"AI Extraction failed: {e}")
                    return

            # 6. Saving
            with st.spinner("Step 4: Saving FIR Draft..."):
                try:
                    fir_id = save_fir_draft(dto, complaint_id, metadata)
                    st.success(f"FIR Draft saved successfully! ID: {fir_id}")
                except Exception as e:
                    st.error(f"Failed to save to database: {e}")
