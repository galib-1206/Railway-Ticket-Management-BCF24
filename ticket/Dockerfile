FROM python:3.12-alpine

LABEL maintainer="Projects BD"

WORKDIR /app/ticket

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --upgrade setuptools \
    && pip install --no-cache-dir gunicorn

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8002", "ticket.wsgi:application"]