# PRO.md

# Project Name

# FIRStruct AI

### Offline AI-Powered Handwritten Complaint to Structured FIR Generator

---

# Overview

FIRStruct AI is an **offline-first, CPU-optimized AI application** designed for police stations and law enforcement agencies to transform **handwritten or printed complaints** into **structured FIR drafts** without requiring an internet connection.

Many police stations still receive complaints on paper. Officers manually read these complaints, identify important details, determine applicable legal sections, and prepare FIRs. This process is time-consuming, error-prone, and difficult to search later.

FIRStruct AI automates this entire workflow locally.

The application scans handwritten complaints, extracts text using offline OCR, identifies important legal entities using a lightweight local language model, generates a structured FIR draft, stores everything locally in SQLite, and enables instant searching of previous complaints.

No cloud.
No internet.
No external APIs.

Everything runs completely on the local machine.

---

# Problem Statement

Police departments continue to rely on handwritten complaints for crime reporting.

Current challenges include:

* Manual reading of handwritten complaints
* Time-consuming FIR preparation
* Human errors while extracting important information
* Difficulty searching previous complaints
* Sensitive citizen information uploaded to cloud-based AI tools
* Poor digitization in rural police stations
* Limited internet connectivity in remote areas

---

# Objective

Build an offline AI assistant capable of converting unstructured handwritten complaints into structured FIR information.

Instead of manually reading multiple pages, officers receive a structured report containing:

* Victim Details
* Accused Details
* Incident Summary
* Crime Type
* Date
* Time
* Location
* Vehicle Numbers
* Weapons Used
* Witnesses
* Suggested IPC/BNS Sections
* FIR Draft

Everything remains stored locally.

---

# Key Features

## 100% Offline

Works without internet.

No cloud APIs.

No data sharing.

---

## Handwritten OCR

Supports:

* Handwritten complaints
* Printed complaints
* Scanned PDFs
* Mobile camera images

---

## AI Information Extraction

Automatically extracts:

* Victim Name
* Father's Name
* Gender
* Age
* Address
* Phone Number
* Aadhaar (optional)
* Accused Name
* Crime Type
* Incident Date
* Incident Time
* Incident Location
* Vehicle Numbers
* Weapons Used
* Stolen Property
* Amount Lost
* Witnesses
* Police Station Jurisdiction
* Suggested IPC/BNS Sections

---

## Automatic FIR Draft Generation

Instead of writing FIRs manually, officers receive a ready-to-review FIR draft.

---

## Local Database

Stores extracted FIRs inside SQLite.

Allows searching by:

* Victim
* Accused
* Crime Type
* Date
* Location
* Vehicle Number
* IPC/BNS Sections

---

## Smart Search

Example queries:

* Find robbery cases in Hyderabad
* Find all bike thefts
* Search complaints involving knife attacks
* Show all FIRs against a person

---

## PDF Export

Export FIR as:

* PDF
* JSON
* CSV

---

# High-Level Workflow

```text
Handwritten Complaint
        │
        ▼
Camera / Scanner Upload
        │
        ▼
Image Enhancement
(OpenCV)
        │
        ▼
Offline OCR
(PaddleOCR)
        │
        ▼
Raw Complaint Text
        │
        ▼
Text Cleaning
        │
        ▼
Local LLM
(Ollama)
        │
        ▼
Entity Extraction
        │
        ▼
Structured JSON
        │
        ▼
FIR Draft Generator
        │
        ▼
SQLite Database
        │
        ▼
Search Dashboard
```

---

# Processing Pipeline

## Step 1

Upload handwritten complaint.

Supported formats:

* JPG
* PNG
* PDF
* Camera Scan

---

## Step 2

Image preprocessing using OpenCV.

Operations:

* Noise Removal
* Contrast Enhancement
* Deskew
* Thresholding
* Sharpening

---

## Step 3

Offline OCR converts handwriting into text.

Recommended OCR:

* PaddleOCR
* TrOCR
* EasyOCR

---

## Step 4

Clean OCR output.

Remove:

* Duplicate spaces
* OCR mistakes
* Broken sentences

---

## Step 5

Send cleaned text to a local LLM.

Recommended Models:

* Phi-3 Mini
* Qwen2.5:3B
* Gemma 3 4B
* TinyLlama

Prompt:

"Extract all legal entities and return ONLY valid JSON."

---

## Step 6

Generated JSON

```json
{
  "victim": "Ravi Kumar",
  "accused": "Unknown",
  "date": "27-06-2026",
  "time": "8:30 PM",
  "location": "Secunderabad Railway Station",
  "crime_type": "Robbery",
  "vehicle": "AP09AB1234",
  "weapon": "Knife",
  "stolen_items": [
    "Motorcycle"
  ],
  "sections": [
    "Relevant BNS Sections"
  ],
  "summary": "Victim attacked by three unknown persons and motorcycle stolen."
}
```

---

## Step 7

Generate structured FIR draft.

Officer only reviews and approves.

---

## Step 8

Store locally.

SQLite

No cloud.

---

# Tech Stack

| Component            | Technology              |
| -------------------- | ----------------------- |
| Programming Language | Python 3.12             |
| Frontend             | Streamlit               |
| OCR                  | PaddleOCR               |
| Image Processing     | OpenCV                  |
| Local AI             | Ollama                  |
| Models               | Phi-3 Mini / Qwen2.5:3B |
| Database             | SQLite                  |
| Search               | FAISS (Optional)        |
| Export               | ReportLab               |

---

# Project Structure

```
firstruct-ai/

app.py

frontend/
    dashboard.py
    upload.py
    history.py
    search.py

ocr/
    image_preprocessing.py
    paddle_reader.py

processing/
    cleaner.py
    parser.py

ai/
    prompt.py
    extractor.py
    validator.py

fir/
    generator.py

database/
    sqlite.py

schemas/
    fir_schema.py

exports/
    pdf_export.py

cache/

tests/

requirements.txt
```

---

# Database Schema

## FIR Table

* id
* victim_name
* accused_name
* crime_type
* incident_date
* incident_time
* location
* vehicle_number
* ipc_sections
* summary
* fir_json
* created_at

---

# Future Enhancements

* Voice Complaint → FIR
* Regional Language Support
* Crime Hotspot Mapping
* Offline Face Sketch Generation
* Signature Detection
* Court Charge Sheet Drafting
* Police Analytics Dashboard
* Multi-language OCR
* Duplicate Complaint Detection
* Criminal History Matching
* Offline Evidence Management

---

# Expected Impact

* Faster FIR registration
* Reduced manual paperwork
* Better crime record digitization
* Improved officer productivity
* Works in rural police stations
* Protects sensitive citizen data
* No dependency on internet
* Low hardware requirements

---

# Why This Project?

Unlike existing cloud-based AI solutions, FIRStruct AI is specifically designed for government environments where privacy, offline capability, and low-cost deployment are essential.

By combining offline OCR, lightweight local language models, and structured legal information extraction, the system significantly reduces the time required to convert handwritten complaints into searchable digital FIRs while ensuring all data remains securely on the local device.
