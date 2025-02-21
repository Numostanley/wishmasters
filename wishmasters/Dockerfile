FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install wheel

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]

EXPOSE 8000
