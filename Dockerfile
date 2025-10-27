# 1️⃣ Use official Python image as the base
FROM python:3.11-slim

# 2️⃣ Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3️⃣ Set working directory in the container
WORKDIR /app

# 4️⃣ Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 5️⃣ Copy dependency list (requirements.txt) into container
COPY requirements.txt /app/

# 6️⃣ Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 7️⃣ Copy the entire backend project into the container
COPY . /app/

# 8️⃣ Expose Django's default port
EXPOSE 8000

# 9️⃣ Command to run Django ASGI server with daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "netguardian.asgi:application"]
