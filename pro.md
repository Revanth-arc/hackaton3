Project Name

PaperLens (or) ResearchIQ Offline (or) PaperStruct AI

An offline AI-powered research paper analyzer that extracts structured knowledge from academic papers and builds a searchable local knowledge base.

Problem Statement

Researchers and students spend significant time reading lengthy research papers to identify key information such as objectives, methodology, datasets, results, limitations, and future work.

Most existing AI assistants require an internet connection and upload sensitive research documents to cloud services, making them unsuitable for confidential or offline environments.

This project provides an offline-first, CPU-optimized solution that transforms research papers into structured, searchable data entirely on the user's device.

Objective

Convert an unstructured research paper (PDF) into structured information using only local AI.

Instead of this:

50-page PDF

You get:

Title
Authors
Abstract
Keywords
Problem Statement
Methodology
Dataset Used
Algorithms
Results
Limitations
Future Work
References

Everything stored locally.

High-Level Workflow
                PDF Upload
                     │
                     ▼
          Extract PDF Text
                     │
                     ▼
          Clean & Normalize Text
                     │
                     ▼
       Local Small Language Model
                     │
                     ▼
          Structured JSON Output
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
      SQLite Database       Search Index
          │                     │
          └──────────┬──────────┘
                     ▼
             Streamlit Dashboard
Input

Supported

Research Paper PDF
Conference Paper
IEEE papers
Springer papers
ACM papers
arXiv PDFs

Future

DOCX
Scanned PDFs
Images
Processing Pipeline
Step 1

Upload PDF

↓

PyMuPDF

↓

Extract text

Step 2

Normalize

Remove

headers
footers
page numbers
repeated spaces
broken lines
Step 3

Chunk the paper

Instead of sending 20 pages at once

Split into

Abstract

Introduction

Related Work

Methodology

Experiments

Results

Conclusion

Much better for small local models.

Step 4

LLM Extraction

Prompt example

Extract the following fields.

Return ONLY valid JSON.

Fields:

Title

Authors

Institution

Research Domain

Keywords

Problem Statement

Methodology

Dataset

Algorithms

Evaluation Metrics

Results

Limitations

Future Work

References
Step 5

Validate JSON

If invalid

Retry

If still invalid

Report error

Step 6

Store in SQLite

JSON Schema

Example

{
  "paper_id": "001",

  "title": "Attention Is All You Need",

  "authors": [
    "Ashish Vaswani",
    "Noam Shazeer"
  ],

  "institution": [
    "Google Brain"
  ],

  "publication_year": 2017,

  "domain": "Natural Language Processing",

  "keywords": [
    "Transformer",
    "Attention",
    "Neural Networks"
  ],

  "problem_statement":
    "Sequence modeling using recurrence is inefficient.",

  "methodology":
    "Transformer architecture",

  "datasets":[
      "WMT14 English-German"
  ],

  "algorithms":[
      "Transformer"
  ],

  "evaluation_metrics":[
      "BLEU"
  ],

  "results":"State-of-the-art translation accuracy",

  "limitations":"Requires large datasets",

  "future_work":"Scaling Transformer models",

  "summary":"Introduced attention-only architecture."
}
SQLite Tables
Papers
id

title

authors

year

domain

summary

json

created_at
Keywords
paper_id

keyword
Datasets
paper_id

dataset
Algorithms
paper_id

algorithm
UI
Dashboard
Upload Paper

────────────

Paper Preview

────────────

Extracted Metadata

────────────

Summary

────────────

Keywords

────────────

Future Work

────────────

Save
History
Previously Uploaded Papers

Search

Filter

Sort

Open

Delete
Search

Search by

Author

Year

Keyword

Algorithm

Dataset

Domain
Nice Features
Paper Comparison

Upload

Paper A

Paper B

↓

Generate

Common topic

Different methodology

Different datasets

Performance comparison
Knowledge Graph
Transformer

↓

Used by

↓

Paper A

↓

Paper B

↓

Paper C
Local Chat

Ask

Which paper used CIFAR-10?

or

Find papers using reinforcement learning.

Uses

SQLite + optional FAISS.

Export

Export

JSON

CSV

Markdown Summary
Folder Structure
paperlens/

│

├── app.py

├── frontend/

│      dashboard.py

│      upload.py

│      search.py

│      history.py

│

├── ingestion/

│      pdf_reader.py

│      parser.py

│

├── processing/

│      cleaner.py

│      chunker.py

│

├── ai/

│      prompt.py

│      extractor.py

│      validator.py

│

├── database/

│      sqlite.py

│      models.py

│

├── schemas/

│      paper_schema.py

│

├── utils/

│

├── cache/

│

└── tests/
Tech Stack
Component	Tool
Frontend	Streamlit
PDF Parsing	PyMuPDF
OCR (optional)	EasyOCR
Local LLM	Ollama
Model	Qwen2.5:3B / Phi-3 Mini
Database	SQLite
Semantic Search (optional)	FAISS
Language	Python
Deployment	Local / Docker
Why This Fits the Hackathon
Hackathon Requirement	Solution
Offline-first	All processing runs locally; no internet required after setup.
CPU-first	Uses lightweight quantized local models (e.g., Qwen2.5:3B or Phi-3 Mini) through Ollama.
Unstructured → Structured	Converts PDF text into a well-defined JSON schema.
Local Storage	Persists extracted data in SQLite (and optionally FAISS for semantic search).
Resource Efficiency	Chunk-based processing avoids loading entire documents into the model at once.
Data Schema Alignment	Consistent JSON schema for every processed paper.
Extensibility	Can later support scanned PDFs (OCR), audio lectures (Whisper.cpp), or research presentations without redesigning the architecture.