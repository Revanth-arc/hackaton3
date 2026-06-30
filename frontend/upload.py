import logging

import streamlit as st

from batch.batch_processor import process_single_file

logger = logging.getLogger(__name__)


def render_upload_page():
    st.header("Upload Handwritten or Digital Complaints")

    # Accept multiple files
    uploaded_files = st.file_uploader(
        "Choose files (PDF, JPG, PNG)",
        type=["pdf", "jpg", "jpeg", "png"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        st.subheader(f"Queue ({len(uploaded_files)} files)")

        # Display Queue
        for f in uploaded_files:
            file_size_kb = f.size / 1024
            st.text(f"⏳ {f.name} ({file_size_kb:.2f} KB)")

        if st.button("Process Batch"):
            progress_text = "Processing Batch..."
            progress_bar = st.progress(0, text=progress_text)

            results = []

            total_files = len(uploaded_files)
            for i, uploaded_file in enumerate(uploaded_files):
                file_bytes = uploaded_file.read()
                filename = uploaded_file.name

                # Update main progress bar
                progress_bar.progress(
                    i / total_files,
                    text=f"Processing Image {i+1} of {total_files}: {filename}",
                )

                st.write(f"### Processing: {filename}")

                def pdf_progress(current, total, status):
                    pass  # We can just let the main progress indicate which file we are on

                with st.spinner(f"Extracting & processing {filename}..."):
                    result = process_single_file(file_bytes, filename, pdf_progress)
                    results.append(result)

                    if result["status"] == "success":
                        st.success(
                            f"✓ {filename} Processed Successfully! (FIR ID: {result['fir_id']})"
                        )
                        with st.expander(f"View Results for {filename}"):
                            st.json(result["json"])
                            st.text_area(
                                "OCR Text",
                                result["raw_text"],
                                height=150,
                                key=f"text_{i}",
                            )
                    elif result["status"] == "cached":
                        st.info(f"✓ {filename} was already processed (cached).")
                        with st.expander(f"View Cached Results for {filename}"):
                            st.json(result["data"])
                    else:
                        st.error(
                            f"✗ {filename} failed during {result.get('step')}: {result.get('error')}"
                        )

            progress_bar.progress(1.0, text="Batch Processing Complete!")

            success_count = sum(1 for r in results if r["status"] in ["success", "cached"])
            fail_count = total_files - success_count

            st.subheader("Batch Summary")
            st.write(
                f"**Total:** {total_files} | **Success:** {success_count} | **Failed:** {fail_count}"
            )
            st.info("You can view all processed complaints in the History & Search tab.")
