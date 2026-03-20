FROM python:3.11-slim AS deps
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --user --no-cache-dir -r /app/requirements.txt

FROM python:3.11-slim AS api
WORKDIR /app
COPY --from=deps /root/.local /root/.local
COPY . /app
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.11-slim AS worker
WORKDIR /app
COPY --from=deps /root/.local /root/.local
COPY . /app
ENV PATH=/root/.local/bin:$PATH
RUN playwright install chromium
CMD ["python", "-m", "arq", "backend.worker.WorkerSettings"]
