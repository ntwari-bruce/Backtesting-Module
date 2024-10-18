FROM python:3.12-slim

WORKDIR /app

# Install required dependencies, including the Cloud SQL proxy
RUN apt-get update \
    && apt-get install -y libpq-dev gcc curl netcat-openbsd \
    && curl -o /cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 \
    && chmod +x /cloud_sql_proxy \
    && apt-get clean

# Copy the requirements.txt file into the container
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entrypoint.sh script into the container
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Expose port 8000 for Django
EXPOSE 8080

# Run the app using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "financial_system.wsgi:application"]

