# Clinical Trial Qualifier

An intelligent system for matching patients to clinical trials while maintaining privacy and HIPAA compliance through automated PHI redaction and AI-powered qualification.

## Overview

This project automates the process of qualifying patients for clinical trials by:
1. Processing patient medical records (EHR data)
2. Protecting patient privacy through automated PHI redaction
3. Using AI agents to match patients with relevant clinical trials
4. Evaluating inclusion/exclusion criteria programmatically

## Workflow

### 1. Patient Record Upload
Upload PDF documents containing patient records (pseudo EHR data) for processing.

### 2. PHI Redaction with Skyflow Detect
Patient records are ingested using **Skyflow Detect** to automatically identify and redact Protected Health Information (PHI), creating a privacy-compliant redacted record.

### 3. Claude Agent Processing
The redacted patient record is passed to a **Claude AI agent** for intelligent analysis and matching.

### 4. Clinical Trial Retrieval
The agent queries the **Clinical Trials MCP (Model Context Protocol)** to retrieve potentially relevant clinical trials based on the patient's medical profile.

### 5. Qualification via Subagent
A specialized **subagent tool** evaluates the patient record against each trial's:
- Inclusion criteria
- Exclusion criteria

This determines which trials the patient qualifies for.

### 6. Optimization Loop
The agent evaluates whether the current set of trials is optimal or if additional MCP queries are needed to find better matches.

### 7. Results
Returns a curated set of qualified clinical trials that match the patient's profile and meet all eligibility criteria.

## Key Features

- **Privacy-First**: Automated PHI redaction ensures HIPAA compliance
- **Intelligent Matching**: Claude AI agents understand complex medical criteria
- **Iterative Optimization**: Agent can refine trial searches for optimal matches
- **Structured Evaluation**: Systematic assessment of inclusion/exclusion criteria

## Technologies

- **Skyflow Detect**: PHI detection and redaction
- **Claude AI**: Intelligent agent orchestration
- **Clinical Trials MCP**: Clinical trial database access
- **Subagent Architecture**: Specialized qualification logic
- **FastAPI**: Modern, high-performance Python web framework
- **Uvicorn**: ASGI server for FastAPI
- **HTML/CSS/JavaScript**: User interface

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd clinicaltrialqualifier
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

**Option 1: Using the startup script (recommended)**
```bash
./run.sh
```

**Option 2: Using uvicorn directly**
```bash
source venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

**Option 3: Using Python directly**
```bash
source venv/bin/activate
python app.py
```

Once running:
1. Open your browser and navigate to: `http://localhost:5000`
2. Enter medical information in the text box
3. Click "De-identify Information" to see PHI automatically redacted

**Bonus**: FastAPI provides interactive API documentation at:
- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

### Example Usage

Try entering sample medical information like:
```
Patient John Smith, DOB 03/15/1975, SSN 123-45-6789, lives at 123 Main Street, Boston MA. 
Phone: 555-1234. Medical Record #: MRN-987654
```

The system will automatically detect and redact:
- Names
- Dates of birth
- Social Security Numbers
- Addresses
- Phone numbers
- Medical record numbers

## Use Cases

- Streamlining clinical trial recruitment
- Helping patients find suitable trials
- Reducing manual review time for trial coordinators
- Improving trial enrollment rates through better matching

---

*This project demonstrates the intersection of privacy-preserving technologies, AI agents, and healthcare data to solve real-world clinical challenges.*

