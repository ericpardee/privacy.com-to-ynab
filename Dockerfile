# Use an official Python runtime as the parent image
FROM python:3.11-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Define an environment variable
# This is a typical way to pass flags to a command line script
ENV DEBUG=false

# Run the script when the container launches
CMD ["python", "app.py"]
