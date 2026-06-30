FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py config.py database.py ./
COPY bot/ bot/
COPY services/ services/
COPY scripts/ scripts/

RUN mkdir -p data credentials

CMD ["python", "main.py"]
