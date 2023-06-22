FROM debian:11

RUN apt update && apt upgrade -y
RUN apt install -y python3-pip default-libmysqlclient-dev
RUN pip install flask flask-mysqldb uvicorn

WORKDIR /srv
COPY app.py app.py

CMD uvicorn app:app --host 127.0.0.1
