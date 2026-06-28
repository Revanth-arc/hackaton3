# FIRStruct AI 

### Offline AI-Powered Handwritten Complaint to Structured FIR Generator

An **offline-first, CPU-optimized AI application** designed for police stations and law enforcement agencies to transform **handwritten or printed complaints** into **structured FIR drafts** without requiring an internet connection.

## 🎯 Problem Statement

Police departments continue to rely on handwritten complaints for crime reporting. Current challenges include:
- Manual reading of handwritten complaints is time-consuming and error-prone.
- Preparing FIRs takes significant time away from field work.
- It is difficult to digitally search past handwritten complaints.
- Sensitive citizen information cannot be securely uploaded to cloud-based AI tools.
- Limited internet connectivity in rural police stations limits tech adoption.

FIRStruct AI automates this entire workflow securely and entirely on the local machine.

## 🚀 Objective

Build an offline AI assistant capable of converting unstructured handwritten complaints into structured FIR information. Instead of manually reading multiple pages, officers receive a structured report containing:
- Victim & Accused Details
- Incident Summary, Crime Type, Date, Time, Location
- Vehicle Numbers & Weapons Used
- Suggested IPC/BNS Sections
- A ready-to-review FIR Draft

**Everything is stored locally. No cloud. No internet. No external APIs.**

## ✨ Key Features
- **100% Offline**: Works without internet. No data sharing. Ensures absolute privacy.
- **Handwritten OCR**: Supports handwritten complaints, printed complaints, scanned PDFs, and mobile camera images using PaddleOCR.
- **Image Enhancement**: Cleans up noisy mobile scans using OpenCV before text extraction.
- **AI Information Extraction**: Automatically extracts legal entities using lightweight local language models (Ollama).
- **Automatic FIR Draft Generation**: Officers receive a ready-to-review FIR draft.
- **Smart Search**: Search past complaints by victim, accused, crime type, location, vehicle, or weapon via SQLite.
- **PDF Export**: Generate printable FIR PDFs instantly.

## 🛠 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Programming Language** | Python 3.12 |
| **Frontend** | Streamlit |
| **OCR** | PaddleOCR |
| **Image Processing** | OpenCV |
| **Local AI** | Ollama (Phi-3 Mini / Qwen2.5:3B) |
| **Database** | SQLite |
| **PDF Export** | ReportLab |

## 🏗 High-Level Workflow & Pipeline

```mermaid
graph TD
    A[Handwritten Complaint] --> B[Camera / Scanner Upload]
    B --> C[Image Enhancement via OpenCV]
    C --> D[Offline OCR via PaddleOCR]
    D --> E[Raw Complaint Text]
    E --> F[Text Cleaning]
    F --> G[Local LLM via Ollama]
    G --> H[Entity Extraction]
    H --> I[Structured JSON Validation]
    I --> J[FIR Draft Generator]
    J --> K[SQLite Database]
    K --> L[Search Dashboard & PDF Export]
```

## 📂 Project Structure

```
firstruct-ai/
├── app.py                  # Main Streamlit entry point
├── frontend/               # Streamlit UI pages
│   ├── dashboard.py
│   ├── upload.py
│   ├── history.py
│   └── search.py
├── ocr/                    # Image processing and text extraction
│   ├── image_preprocessing.py
│   └── paddle_reader.py
├── processing/             # Text cleaning
│   ├── cleaner.py
│   └── parser.py
├── ai/                     # LLM inference and validation
│   ├── prompt.py
│   ├── extractor.py
│   └── validator.py
├── database/               # Database management
│   └── sqlite.py
├── schemas/                # JSON output schemas
│   └── fir_schema.py
├── exports/                # Report generation
│   └── pdf_export.py
├── cache/                  # File caching
├── tests/                  # Unit and integration tests
└── requirements.txt
```

## 📊 Database Schema (SQLite)

**FIR Table:**
- `id`, `victim_name`, `accused_name`, `crime_type`, `incident_date`, `incident_time`, `location`, `vehicle_number`, `ipc_sections`, `summary`, `fir_json`, `created_at`

## 🔮 Future Enhancements
- Voice Complaint → FIR conversion (Whisper.cpp)
- Regional Language Support (Multilingual OCR)
- Crime Hotspot Mapping
- Duplicate Complaint Detection
- Criminal History Matching

## 🚀 Setup & Installation (WIP)

*Instructions on how to install OpenCV, PaddleOCR, pull the Ollama model, and run the Streamlit app will go here.*
