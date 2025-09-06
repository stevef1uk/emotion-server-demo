# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the UI application
COPY ui.py .

# Create a non-root user
RUN useradd -m -u 1000 uiuser && chown -R uiuser:uiuser /app
USER uiuser

# Expose the port Gradio will run on
EXPOSE 7860

# Command to run the Gradio app
CMD ["python", "ui.py"]
