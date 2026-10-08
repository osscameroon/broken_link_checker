# Install uv
FROM python:3.14-slim AS builder

# Change the working directory to the `app` directory
WORKDIR /app

# Copy the project into the intermediate image
COPY . /app

# Install dependencies
RUN pip install . --no-cache

ENTRYPOINT ["python", "-m", "blc"]
