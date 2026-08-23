#!/bin/bash
cd /Users/mani/Documents/bookxpert
source venv/bin/activate
streamlit run app.py --server.port 8501 --server.headless true
