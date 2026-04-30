FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy pyproject.toml and install dependencies
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-install-project

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Run the application (remove --reload for production)
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]