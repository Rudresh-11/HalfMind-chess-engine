# 1️⃣ Base image (small & fast)
FROM python:3.11-slim

# 2️⃣ Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3️⃣ Set working directory
WORKDIR /app

# 4️⃣ Install system deps (needed for python-chess performance)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5️⃣ Copy requirements first (cache optimization)
COPY requirements.txt .

# 6️⃣ Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 7️⃣ Copy project files
COPY . .

# 8️⃣ Expose port
EXPOSE 5000

# 9️⃣ Run with Gunicorn (production server)
CMD ["gunicorn", "-w", "1", "-t", "120", "-b", "0.0.0.0:5000", "app:app"]
