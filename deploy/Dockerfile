# Dockerfile for self-hosted deployment
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .
COPY supervisor/ supervisor/

# Create non-root user
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import aiohttp, asyncio; asyncio.run(aiohttp.ClientSession().get('http://localhost:8000/health').close())"

# Expose port
EXPOSE 8000

# Run the MCP server
CMD ["python", "server.py"]