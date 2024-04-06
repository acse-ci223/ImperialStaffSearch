# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port available to the world outside this container
EXPOSE 80
EXPOSE 8000

# Run frontend.py when the container launches
CMD ["streamlit", "run", "frontend.py", "--server.port=80", "--server.address=0.0.0.0", "--browser.gatherUsageStats=False", "--browser.serverAddress=localhost"]
