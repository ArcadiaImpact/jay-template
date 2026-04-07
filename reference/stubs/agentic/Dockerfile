# STUB: Base image for the sandbox environment.
# Choose an image appropriate for your evaluation tasks.
FROM python:3.12-slim

# STUB: Install any system dependencies your evaluation needs
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# STUB: Install Python packages if needed
# RUN pip install --no-cache-dir numpy pandas

# Run as non-root user for security
RUN useradd -m -s /bin/bash agent
USER agent
WORKDIR /home/agent
