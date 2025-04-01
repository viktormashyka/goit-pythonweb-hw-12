# Dockerfile

# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install system dependencies and Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    iproute2 \
    libpq-dev \
    gcc \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application code
COPY . .

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app

# Create a non-root user and set ownership
RUN useradd -m appuser && chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose the port that the app runs on
EXPOSE 8000

# Command to run the application (use --reload only for dev)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
