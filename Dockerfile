# ---------- BUILDER STAGE ----------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install ALL dependencies (including grpcio-tools for proto generation)
RUN pip install --no-cache-dir -r requirements.txt

# Copy proto files
COPY protos ./protos

# Generate gRPC Python code
RUN mkdir -p app/generated && \
    find ./protos -name "*.proto" -exec python -m grpc_tools.protoc \
    -I ./protos \
    --python_out=. \
    --grpc_python_out=. \
    {} \;

# ---------- RUNTIME STAGE ----------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser

# Copy requirements and install (IMPORTANT: includes grpcio + protobuf)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy generated proto files
COPY --from=builder /app/app/generated ./app/generated

# Copy application code
COPY database.py grpc_server.py handlers.py main.py models.py schema.py ./

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8000
EXPOSE 50051

# Start FastAPI (you can also start gRPC inside main.py)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]