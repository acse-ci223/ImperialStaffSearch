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

FROM nginx:1.19.1-alpine

RUN apk update && \
    apk add --no-cache openssl && \
    openssl req -x509 -nodes -days 365 \
    -subj  "/C=CA/ST=QC/O=Company Inc/CN=iclstaff.com" \
     -newkey rsa:2048 -keyout key.pem \
     -out cert.pem;

# Run frontend.py when the container launches
# CMD ["streamlit", "run", "frontend.py", "--browser.serverAddress=localhost"]
# streamlit run app.py --server.enableCORS=false --server.sslKeyFile /tmp/key.pem --server.sslCertFile /tmp/cert.pem
CMD ["streamlit", "run", "frontend.py", "--server.enableCORS=false", "--server.sslKeyFile", "key.pem", "--server.sslCertFile", "cert.pem"]
