FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY train_model.py .
COPY data ./data

CMD ["python", "train_model.py", "--train-path", "data/train.csv", "--test-path", "data/test.csv", "--output-dir", "/shared"]
