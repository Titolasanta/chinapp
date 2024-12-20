# Use the official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app/


# Expose the port that the app will run on
EXPOSE 8080

# Set the command to run the Django app using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "chinp.wsgi:application"]