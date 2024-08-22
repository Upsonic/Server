FROM ubuntu

LABEL org.opencontainers.image.source https://github.com/Upsonic/Server

RUN mkdir /app
RUN mkdir /db

RUN apt-get update
RUN apt-get install python3 python3-pip -y
RUN apt-get install nginx redis-server -y
RUN apt-get install openssl -y
RUN apt-get install git -y
RUN apt-get install curl -y

WORKDIR /app/

COPY Server/requirements.txt /requirements.txt
COPY Server/ollama_install.sh /ollama_install.sh
RUN pip3 install -r /requirements.txt --break-system-packages
RUN sh /ollama_install.sh
RUN (ollama serve &) && sleep 30 && ollama pull phi3.5 && ollama pull nomic-embed-text

COPY Server Server

COPY Server/the.conf /etc/nginx/conf.d/the.conf

COPY Server/run.sh /

COPY models Server/upsonic_on_prem/api/utils/ai/

WORKDIR /app/Server

EXPOSE 7340
EXPOSE 7341

CMD ["bash", "/run.sh"]
