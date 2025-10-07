# ---------- Builder ----------
FROM python:3.11-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# System basics (kept minimal). Build tools only in builder.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements for wheel build
COPY requirements.txt ./

# Ensure modern pip/setuptools; build all wheels including transitive deps
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip wheel --no-cache-dir -r requirements.txt -w /wheels

# ---------- Runtime ----------
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# Non-root user
RUN useradd -m appuser

# Install from wheels only (offline, reproducible)
COPY --from=builder /wheels /wheels
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
 && rm -rf /wheels

# App code and data
COPY src ./src
COPY data ./data

USER appuser
CMD ["python", "src/data_analysis.py"]
