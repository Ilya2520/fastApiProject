FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY app/requirements_for_test.txt .


RUN pip install --no-cache-dir -r requirements_for_test.txt

COPY . .

CMD ["pytest", "-vv"]
