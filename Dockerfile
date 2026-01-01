FROM python:3.11-slim

ENV PYTHONUNBUFFERED True
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy everything first to avoid path confusion
COPY . .

# Troubleshooting: list files to see where requirements.txt is
RUN ls -R

# Install from the known location
RUN pip install --no-cache-dir -r etf_tracker/requirements.txt

ENV PORT 8080
EXPOSE 8080

CMD ["streamlit", "run", "etf_tracker/app.py", "--server.port=8080", "--server.address=0.0.0.0"]
