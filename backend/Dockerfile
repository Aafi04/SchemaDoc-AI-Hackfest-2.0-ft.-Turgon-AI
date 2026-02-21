FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY shared/ ./shared/

# Copy data directory (usage logs for ReAct tool)
RUN mkdir -p data
COPY data/usage_logs.sql ./data/usage_logs.sql

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
