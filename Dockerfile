# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install net-tools and other dependencies
RUN apt-get update && apt-get install -y net-tools && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Copy SSL certificates into the container
COPY ssl/client-cert.pem /app/ssl/client-cert.pem
COPY ssl/client-key.pem /app/ssl/client-key.pem

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application with a delay to ensure dependencies are ready
CMD ["sh", "-c", "sleep 60 && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
