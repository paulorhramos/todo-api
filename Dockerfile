FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .
COPY init_db.py .

# Expose port
EXPOSE 5000

# Initialize database and run with gunicorn
CMD python init_db.py && gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 60 app:app
