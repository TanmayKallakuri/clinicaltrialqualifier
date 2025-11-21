#!/bin/bash

# Activate virtual environment and run the FastAPI app
cd "$(dirname "$0")"
source venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 5000 --reload

