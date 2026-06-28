You are an experienced software engineer participating in a hackathon.

Your task is to build an OFFLINE-FIRST, CPU-OPTIMIZED AI application that converts unstructured data into structured JSON and stores it locally.

The application MUST follow the hackathon requirements below.

==================================================
HACKATHON OBJECTIVE
==================================================

Build a local AI pipeline that accepts unstructured input and transforms it into structured, actionable data.

The entire pipeline must work WITHOUT INTERNET.

No cloud inference.
No external APIs.
No OpenAI.
No Anthropic.
No Gemini APIs.

Every AI operation must execute locally on the user's machine.

==================================================
PROJECT SCOPE
==================================================

For the MVP, choose ONE input modality.

Preferred option:

PDF + Images

The application should accept:

• PDF files
• Scanned documents
• Images
• Receipts
• Invoices

Future architecture should make it easy to add:

• Audio
• Video
• Text files

==================================================
EXPECTED PIPELINE
==================================================

User uploads document/image

↓

Extract text

↓

Normalize text

↓

Local Small Language Model

↓

Generate structured JSON

↓

Validate JSON

↓

Store in SQLite

↓

Allow searching/viewing stored data

==================================================
TECH STACK
==================================================

Language:
Python 3.12+

Frontend:
Streamlit

Local LLM:
Ollama

Preferred models:

- Qwen2.5
- Phi-3 Mini
- Gemma
- TinyLlama

Do NOT use cloud models.

OCR:

EasyOCR

or

Tesseract OCR

PDF Reading:

PyMuPDF

or

pdfplumber

Database:

SQLite

Optional:

FAISS or ChromaDB for semantic search

==================================================
PROJECT STRUCTURE
==================================================

Use clean architecture.

Suggested structure:

project/

    app.py

    frontend/

    backend/

    ingestion/

        pdf_reader.py

        image_reader.py

        ocr.py

    processing/

        cleaner.py

        normalizer.py

    ai/

        prompt.py

        llm.py

        parser.py

        validator.py

    database/

        sqlite.py

        models.py

    schemas/

        invoice_schema.py

        receipt_schema.py

    utils/

    cache/

    tests/

    requirements.txt

==================================================
INGESTION
==================================================

Support:

• PDF

• PNG

• JPG

• JPEG

Extract text using OCR if necessary.

Handle scanned PDFs.

Gracefully report unreadable files.

==================================================
TEXT NORMALIZATION
==================================================

Clean OCR output.

Remove:

- duplicated spaces

- broken lines

- OCR artifacts

Normalize:

- dates

- currencies

- numbers

- phone numbers

- capitalization

==================================================
LOCAL AI TRANSFORMATION
==================================================

Use Ollama.

The model receives cleaned text.

It must output ONLY valid JSON.

Example:

Input:

Invoice

ABC Electronics

Date: 12-06-2026

Total: ₹4560

GST: ₹696

Expected output:

{
    "company":"ABC Electronics",
    "date":"2026-06-12",
    "total":4560,
    "gst":696
}

Never return markdown.

Never return explanations.

Return JSON only.

==================================================
JSON VALIDATION
==================================================

Validate generated JSON.

If invalid:

Retry automatically.

If still invalid:

Display a useful error message.

==================================================
DATABASE
==================================================

Store extracted JSON in SQLite.

Example table:

documents

id

filename

date

json_data

created_at

Allow viewing previously processed documents.

==================================================
STREAMLIT UI
==================================================

The UI should contain:

Upload document

Preview document

Extracted text

Generated JSON

Save button

History page

Search page

Status/progress indicator

Error messages

==================================================
OFFLINE REQUIREMENTS
==================================================

The application MUST run without internet.

Everything should execute locally.

The only requirement should be that the local model has already been pulled via Ollama.

No online services.

==================================================
CPU OPTIMIZATION
==================================================

Optimize for CPU.

Avoid loading unnecessarily large models.

Stream responses where possible.

Cache expensive operations.

Avoid duplicate OCR.

Use quantized GGUF models when possible.

==================================================
ERROR HANDLING
==================================================

Gracefully handle:

Unreadable PDFs

OCR failure

Model timeout

Invalid JSON

SQLite errors

Missing Ollama model

Display meaningful messages.

Never crash.

==================================================
CACHING
==================================================

Avoid reprocessing identical files.

Hash uploaded files.

If file already exists:

Load cached result.

==================================================
LOGGING
==================================================

Maintain logs for:

OCR

LLM inference

Database

Errors

Processing time

==================================================
NON-FUNCTIONAL REQUIREMENTS
==================================================

Code should be:

Modular

Maintainable

Documented

Type hinted

Easy to extend

Reusable

Avoid monolithic files.

==================================================
DELIVERABLES
==================================================

Produce:

Complete project structure

Well-organized Python modules

requirements.txt

README.md

Setup instructions

Architecture diagram (Markdown)

Database schema

Prompt templates

Example documents

Sample outputs

==================================================
BONUS FEATURES
==================================================

If time permits, implement:

Semantic search using FAISS

Duplicate document detection

Export JSON

Export CSV

Dark mode

Batch document processing

==================================================
CODING STYLE
==================================================

Use modern Python.

Follow PEP8.

Use classes where appropriate.

Keep functions small.

Avoid hardcoded values.

Write reusable components.

Add comments only where necessary.

==================================================
IMPORTANT
==================================================

Think like a senior software architect.

Prioritize:

1. Offline reliability

2. CPU efficiency

3. Clean architecture

4. Modular code

5. Future extensibility

Generate production-quality code instead of hackathon-quality shortcuts whenever possible.
