import json

import pandas as pd
import streamlit as st

from database.repository import (
    delete_complaint,
    get_all_complaints,
    get_complaint_by_id,
    get_statistics,
    search_complaints,
)


def render_history_page():
    st.title("History & Search")

    if "view_complaint_id" not in st.session_state:
        st.session_state.view_complaint_id = None

    if st.session_state.view_complaint_id:
        if st.button("← Back to History"):
            st.session_state.view_complaint_id = None
            st.rerun()
        render_complaint_details(st.session_state.view_complaint_id)
        return

    # Statistics Dashboard
    stats = get_statistics()
    cols = st.columns(5)
    cols[0].metric("Total Complaints", stats["total"])
    cols[1].metric("Today's Complaints", stats["today"])
    cols[2].metric("Unique Crimes", stats["unique_crimes"])
    cols[3].metric("Top Crime", stats["top_crime"])
    cols[4].metric("Top Location", stats["top_location"])

    st.divider()

    # Filters & Search
    st.sidebar.subheader("Filters")
    all_complaints = get_all_complaints()
    crime_types = ["All"] + sorted(
        list(set([c["crime_type"] for c in all_complaints if c["crime_type"]]))
    )
    selected_crime = st.sidebar.selectbox("Crime Category", crime_types)

    statuses = ["All", "Draft", "Processed", "Approved"]
    selected_status = st.sidebar.selectbox("Processing Status", statuses)

    search_query = st.text_input(
        "🔍 Search across complaints (ID, Name, Location, Summary, Vehicles)...", ""
    )

    filters = {"crime_type": selected_crime, "status": selected_status}

    if search_query or selected_crime != "All" or selected_status != "All":
        complaints = search_complaints(search_query, filters)
    else:
        complaints = all_complaints

    if not complaints:
        st.info("No complaints found.")
        return

    colA, colB = st.columns([8, 2])
    with colA:
        st.subheader("Complaint Records")
    with colB:
        df = pd.DataFrame(complaints)
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Export All (CSV)",
            data=csv,
            file_name="all_complaints.csv",
            mime="text/csv",
        )

    # Pagination
    items_per_page = 20
    total_pages = max(1, (len(complaints) - 1) // items_per_page + 1)
    if "page_number" not in st.session_state:
        st.session_state.page_number = 1

    if total_pages > 1:
        st.session_state.page_number = st.number_input(
            "Page",
            min_value=1,
            max_value=total_pages,
            value=st.session_state.page_number,
        )

    start_idx = (st.session_state.page_number - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_data = complaints[start_idx:end_idx]

    hc1, hc2, hc3, hc4, hc5, hc6, hc7 = st.columns([1.5, 2, 2, 2, 2, 1, 1.5])
    hc1.write("**Complaint ID**")
    hc2.write("**Complainant/Victim**")
    hc3.write("**Crime Type**")
    hc4.write("**Location**")
    hc5.write("**Date**")
    hc6.write("**Status**")
    hc7.write("**Actions**")
    st.divider()

    for row in page_data:
        c1, c2, c3, c4, c5, c6, c7 = st.columns([1.5, 2, 2, 2, 2, 1, 1.5])
        # Shorten Complaint ID for display
        short_id = row.get("complaint_id", "")[:8] + "..." if row.get("complaint_id") else ""
        c1.write(short_id)
        c2.write(row.get("victim_name", "") or "Unknown")
        c3.write(row.get("crime_type", "") or "N/A")
        c4.write(row.get("location", "") or "N/A")
        c5.write(row.get("incident_date", "") or "N/A")
        c6.write(row.get("status", ""))

        with c7:
            vc1, vc2 = st.columns(2)
            if vc1.button("👁️", key=f"view_{row['id']}", help="View Details"):
                st.session_state.view_complaint_id = row["id"]
                st.rerun()
            if vc2.button("🗑️", key=f"del_{row['id']}", help="Delete"):
                delete_complaint(row["id"])
                st.success("Deleted!")
                st.rerun()


def render_complaint_details(fir_id):
    st.subheader("Complaint Details")
    details = get_complaint_by_id(fir_id)
    if not details:
        st.error("Complaint not found in database. It may have been deleted.")
        return

    st.write(f"**Database ID:** {details.get('id')}")
    st.write(f"**Complaint ID:** {details.get('complaint_id')}")
    st.write(f"**Processed On:** {details.get('created_at')}")
    st.write(f"**Status:** {details.get('status')}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Primary Entities")
        st.write(f"**Victim/Complainant:** {details.get('victim_name', 'N/A')}")
        st.write(f"**Accused/Suspect:** {details.get('accused_name', 'N/A')}")
        st.write(f"**Crime Type:** {details.get('crime_type', 'N/A')}")
        st.write(f"**Incident Date:** {details.get('incident_date', 'N/A')}")
        st.write(f"**Incident Time:** {details.get('incident_time', 'N/A')}")
        st.write(f"**Location:** {details.get('location', 'N/A')}")

    with col2:
        st.markdown("#### Additional Entities")
        vehicles = details.get("vehicles", [])
        weapons = details.get("weapons", [])
        items = details.get("stolen_items", [])
        sections = details.get("ipc_sections", [])

        st.write(f"**Vehicles:** {', '.join(vehicles) if vehicles else 'None'}")
        st.write(f"**Weapons:** {', '.join(weapons) if weapons else 'None'}")
        st.write(f"**Stolen Items:** {', '.join(items) if items else 'None'}")
        st.write(f"**IPC Sections:** {', '.join(sections) if sections else 'None'}")

    st.markdown("#### Processing Metadata")
    st.write(f"**Original Filename:** {details.get('filename', 'Unknown')}")
    st.write(f"**File Type:** {details.get('file_type', 'Unknown')}")
    st.write(f"**Page Count:** {details.get('page_count', 1)}")
    st.write(f"**Processing Method:** {details.get('processing_method', 'N/A')}")
    st.write(f"**OCR Required:** {'Yes' if details.get('ocr_required') else 'No'}")

    st.markdown("#### AI Summary")
    st.info(details.get("summary", "No summary available."))

    st.divider()

    # Original Document Preview (mocked or loaded if available)
    st.markdown("#### Document & OCR")
    with st.expander("Original Document Preview", expanded=False):
        # We try to see if an image exists (e.g. if the upload pipeline saved it)
        # Assuming the pipeline does not save it yet, we just handle the missing case gracefully.
        st.info("Original file unavailable (not stored locally).")

    with st.expander("OCR Text Viewer", expanded=False):
        st.info("OCR text unavailable (not stored locally).")

    # Structured JSON
    st.markdown("#### Structured JSON")
    with st.expander("View JSON Payload", expanded=False):
        json_str = json.dumps(details, indent=2)
        st.code(json_str, language="json")
        st.download_button(
            "📥 Download JSON",
            data=json_str,
            file_name=f"complaint_{details.get('id')}.json",
            mime="application/json",
        )
