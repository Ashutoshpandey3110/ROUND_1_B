# Stage 1: The Builder Stage (with internet access)
# This stage installs dependencies and downloads the ML model.
FROM --platform=linux/amd64 python:3.9-slim-buster as builder

WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies. We use --no-cache-dir for a smaller image.
RUN pip install --no-cache-dir -r requirements.txt

# Download the sentence-transformer model from Hugging Face Hub.
# This command automatically saves it to a standard cache location
# that we can copy in the next stage.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# ---

# Stage 2: The Final Stage (no internet access)
# This is the lean, production-ready image that will be submitted.
FROM --platform=linux/amd64 python:3.9-slim-buster

WORKDIR /app

# Copy the necessary cached model and the installed Python packages from the builder stage.
# The faulty /root/.cache/torch line has been REMOVED.
COPY --from=builder /root/.cache/huggingface /root/.cache/huggingface
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copy the application source code
COPY src/ /app/src/

# Set environment variables to point to the cached model, ensuring it runs offline
ENV SENTENCE_TRANSFORMERS_HOME=/root/.cache/huggingface/hub
ENV HF_HOME=/root/.cache/huggingface

# Add the source directory to the Python path
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Define the entry point for the container.
ENTRYPOINT ["python", "-m", "src.__main__"]
