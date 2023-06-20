FROM debian:11
RUN apt update && apt upgrade -y
RUN apt install -y python3-pip
RUN pip install flask uvicorn
WORKDIR /srv # il faut bien sur que ce dossier existe...
COPY app.py app.py
CMD uvicorn app1:app --host 0.0.0.0
