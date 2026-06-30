def detect_file_type(file_bytes: bytes) -> str:
    """
    Detects the mime type of the file bytes.
    If python-magic is not installed, falls back to a simple signature check.
    """
    try:
        import magic

        mime = magic.from_buffer(file_bytes, mime=True)
        return mime
    except ImportError:
        # Fallback signature checks
        if file_bytes.startswith(b"%PDF"):
            return "application/pdf"
        elif file_bytes.startswith(b"\xFF\xD8"):
            return "image/jpeg"
        elif file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        return "application/octet-stream"
