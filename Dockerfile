FROM python:3.10-slim

# Install system dependencies for WeasyPrint (fonts, layout and graphic processing libraries)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libffi-dev \
    shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1

# Command to run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
