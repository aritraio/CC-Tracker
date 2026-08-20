# ==============================================================================
# CC Track API — Production Multi-Stage Dockerfile
# ==============================================================================

# Build Stage
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final Runtime Stage
FROM python:3.11-slim AS runner

WORKDIR /app

# Install runtime dependencies for PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root system user
RUN groupadd -g 1001 cctrack && \
    useradd -u 1001 -g cctrack -s /bin/bash -m cctrack

# Copy dependencies from builder
COPY --from=builder --chown=cctrack:cctrack /root/.local /home/cctrack/.local

# Copy application source code
COPY --chown=cctrack:cctrack . .

# Set environment
ENV PATH=/home/cctrack/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

USER cctrack

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
