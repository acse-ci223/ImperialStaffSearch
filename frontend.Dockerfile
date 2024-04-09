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

RUN ["python", "src/GoogleAnalytics.py"]

# Make port available to the world outside this container
EXPOSE 80
# EXPOSE 443

COPY ssl_certs.sh /usr/src/app
RUN chmod +x ssl_certs.sh
RUN ./ssl_certs.sh

# Run frontend.py when the container launches
CMD ["streamlit", "run", "frontend.py", "--browser.serverAddress=localhost"]
# CMD ["streamlit", "run", "frontend.py", "--server.enableCORS=false", "--server.sslKeyFile", "certs/key.pem", "--server.sslCertFile", "certs/cert.pem"]
