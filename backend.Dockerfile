# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy only the requirements file, to cache the pip install step
COPY requirements.txt /usr/src/app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app

# Make port available to the world outside this container
EXPOSE 8000

# Run backend.py when the container launches
CMD ["python", "backend.py"]
