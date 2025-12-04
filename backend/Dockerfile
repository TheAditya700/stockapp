# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY flaskapp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables
ENV FLASK_APP=flaskapp/app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the app when the container launches
CMD ["/app/entrypoint.sh"]
