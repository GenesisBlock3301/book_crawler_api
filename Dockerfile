## Multi-stage docker

## Stage:1 Base builder stage
FROM python:3.12-slim AS builder

# Create the app directory
RUN mkdir /app

# Set working directory
WORKDIR /app

# Set environmental variable a
# Prevent python from writting pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# copy requirements.txt to host to container for install dependencies.
COPY requirements.txt /app/

#UPGRADE PIP
RUN pip install --upgrade pip

# Run this command to install all dependencies
RUN pip install --no-cache-dir -r requirements.txt

## Stage 2 Production Stage
FROM python:3.12-slim
RUN useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser /app

# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Expose django port
EXPOSE 8000

# Start the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]

