FROM python:3.11

RUN set -ex && \
    apt-get update
RUN apt install -y libsqlite3-mod-spatialite
RUN mkdir -p /src


WORKDIR /src

COPY requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["fastapi", "run", "main.py", "--port", "80", "--reload"]