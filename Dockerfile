# official Python image
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python scripts and data folders into the container
COPY scripts /app/scripts
COPY tests /app/tests
COPY data /app/data

# Set environment variables for MongoDB connection
ENV MONGO_HOST=mongodb \
    MONGO_PORT=27017 \
    MONGO_DB=healthcare_dataset

# Expose the port for the application (if needed, e.g., Flask API)
EXPOSE 5000

# Command to run the Migration script first and then run the tests if successful
CMD ["sh", "-c", "python /app/scripts/Migration.py && pytest /app/tests/migration_test.py"]
