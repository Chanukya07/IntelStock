# IntelStock container image
# Builds a single image that can run either the Streamlit frontend or the
# FastAPI backend depending on the command passed at runtime.
FROM python:3.11-slim

WORKDIR /app

# System deps kept minimal; faiss-cpu and sentence-transformers ship wheels.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt requirements/base.txt
RUN pip install --no-cache-dir -r requirements/base.txt

COPY . .

EXPOSE 8000 8501

# Default to the FastAPI backend. Override the command to run Streamlit:
#   docker run <image> streamlit run frontend/dashboard.py --server.port 8501
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
