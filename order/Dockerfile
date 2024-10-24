FROM python:3.12-alpine

LABEL maintainer="Projects BD"

WORKDIR /app/order

COPY ./order/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --upgrade setuptools \
    && pip install --no-cache-dir gunicorn

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8003", "order.wsgi:application"]