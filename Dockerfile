# official Python image
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python scripts and data folders into the container
COPY scripts /app/scripts
COPY data /app/data
COPY data_clean /app/data_clean

# Set environment variables for MongoDB connection
ENV MONGO_HOST=mongodb \
    MONGO_PORT=27017 \
    MONGO_DB=healthcare_db

# Expose the port for the application (if needed, e.g., Flask API)
EXPOSE 5000

# Command to run the Migration script when the container starts
CMD ["python", "/app/scripts/Migration.py"]
