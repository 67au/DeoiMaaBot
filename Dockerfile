# syntax=docker/dockerfile:1.3

FROM python:3.10-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apk add --no-cache gcc musl-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del gcc musl-dev

COPY intel-map-client intel-map-client
COPY main.py ./
COPY entry_point.sh /usr/local/bin/entry_point.sh

RUN chmod +x /usr/local/bin/entry_point.sh

ENV API_ID ""
ENV API_HASH ""
ENV BOT_TOKEN ""
ENV ADMIN ""

ENTRYPOINT ["/usr/local/bin/entry_point.sh"]

CMD ["python", "main.py"]