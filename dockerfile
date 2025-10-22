FROM python:3.12-slim

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier les scripts
COPY scripts /app/scripts
WORKDIR /app
