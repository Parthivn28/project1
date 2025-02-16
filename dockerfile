# Use an official Python image as a base
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the project directory to /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for FastAPI
EXPOSE 8000

# Set the command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
