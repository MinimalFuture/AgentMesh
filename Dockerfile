FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY . /app/

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Install dependencies
RUN pip install --no-cache-dir -e .

# Create configuration directory
RUN mkdir -p /config

# Set environment variable pointing to config file
ENV CONFIG_PATH=/app/config.yaml

# Set entrypoint
CMD ["/app/entrypoint.sh"]

# 添加环境变量标识Docker容器环境
ENV DOCKER_CONTAINER=true
