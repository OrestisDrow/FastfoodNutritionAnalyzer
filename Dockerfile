# Use Python 3.11.5 slim as base image
FROM python:3.11.5-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements.txt file
COPY requirements.txt .

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . .

# Expose port 80 (for the Dash app)
EXPOSE 80

# Run the main.py script on container launch to initialize the database and start the Dash server
CMD ["python", "src/main.py"]
