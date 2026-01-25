FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Install the package in development mode
RUN pip install --no-cache-dir -e .

# Create directories for data and logs
RUN mkdir -p agent_workspace outputs data logs

EXPOSE 8000

# Default command runs the API server
CMD ["uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "8000"]
