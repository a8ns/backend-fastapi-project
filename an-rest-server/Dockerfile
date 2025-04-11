FROM python:3.13-slim

# Update with curl package and poetry dependencies (build-essential for some packages that need compilation)
RUN apt-get update && \
    apt-get install -y curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add poetry to PATH
ENV PATH="${PATH}:/root/.local/bin"

WORKDIR /api

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* /api/

# Configure poetry to not use a virtual environment in the container
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy source code
COPY ./src /api/

# Command to run the application
# Commented out as in your example
# CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]