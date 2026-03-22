# Use lightweight Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Expose both ports
EXPOSE 8000
EXPOSE 50051

# Start FastAPI (this will also start gRPC via startup event)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]