# 1. Use a lightweight version of Python as the base
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install Chromium browser (the open-source version of Chrome) and necessary OS tools
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy the requirements file and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy our smart worker code into the container
COPY smart_worker.py .

# 6. Command to run when the container starts
CMD ["python", "smart_worker.py"]