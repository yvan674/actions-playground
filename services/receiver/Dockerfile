FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Copy the requirements.txt first to leverage Docker cache
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . /app/

# We expect a volume to be attached at runtime at /shared
# We need to make it part of PYTHONPATH
ENV PYTHONPATH="/shared:/app/src"

# Command to run your application
CMD ["python", "./src/receiver_run.py"]
