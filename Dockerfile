# ==========================================
# STAGE 1: Build the application
# ==========================================
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment for installing dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# STAGE 2: Run the application
# ==========================================
FROM python:3.11-slim AS final

# Metadata
LABEL maintainer="Virtual Assistant Reminder"
LABEL description="RisePyMinder - Scheduled notification system"

# Set working directory
WORKDIR /app

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default timezone (can be overridden in docker-compose.yml or with -e flag)
ENV TIMEZONE=UTC

# Default interval for scheduling (can be overridden in docker-compose.yml or with -e flag)
ENV INTERVAL_SECONDS=3600

# Copy application code
COPY --from=builder /opt/venv /opt/venv

# Add local bin to PATH
ENV PATH=/opt/venv/bin:$PATH

# Create a non-root user for security
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -m -s /sbin/nologin appuser

# Create necessary directories
RUN mkdir -p logs

# Copy the rest of the application code
COPY --chown=appuser:appgroup . ./

# Set permissions for the app directory
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Run scheduler every hour (or as defined by INTERVAL_SECONDS)
CMD ["sh", "-c", "while true; do python main.py; sleep ${INTERVAL_SECONDS}; done"]
