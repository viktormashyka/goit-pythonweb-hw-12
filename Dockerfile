# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app

# Install system dependencies and Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends iproute2 libpq-dev gcc build-essential && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt

# Expose the port that the app runs on
EXPOSE 8000

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]