# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application
# Run the command to start gunicorn server (production server)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "monitoring.wsgi:application"]
