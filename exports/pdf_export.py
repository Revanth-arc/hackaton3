import io
import logging
import sqlite3

from database.sqlite import DB_PATH

logger = logging.getLogger(__name__)


def generate_fir_pdf(fir_id: str) -> bytes:
    """Generates a printable FIR PDF using ReportLab."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError:
        logger.error("ReportLab not installed.")
        return b"PDF Generation requires reportlab"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM firs WHERE id = ?", (fir_id,))
    fir = cursor.fetchone()
    conn.close()

    if not fir:
        raise ValueError("FIR not found")

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, f"FIR Draft - {fir[0]}")
    p.drawString(100, 730, f"Victim: {fir[2]}")
    p.drawString(100, 710, f"Accused: {fir[3]}")
    p.drawString(100, 690, f"Crime Type: {fir[4]}")
    p.drawString(100, 670, f"Date: {fir[5]} Time: {fir[6]}")
    p.drawString(100, 650, f"Location: {fir[7]}")
    p.drawString(100, 630, f"Summary: {fir[8]}")

    p.showPage()
    p.save()

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
