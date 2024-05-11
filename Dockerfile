FROM ubuntu

LABEL org.opencontainers.image.source https://github.com/Upsonic/On-Prem

RUN mkdir /app
RUN mkdir /db

RUN apt-get update
RUN apt-get install python3 python3-pip -y
RUN apt-get install nginx redis-server -y
RUN apt-get install openssl -y
RUN apt-get install git-lfs git -y
RUN apt-get install curl -y

WORKDIR /app/

COPY On-Prem/requirements.txt /requirements.txt
COPY On-Prem/ollama_install.sh /ollama_install.sh
RUN pip3 install -r /requirements.txt --break-system-packages
RUN sh /ollama_install.sh
RUN (ollama serve &) && sleep 30 && ollama pull llama3 && ollama pull nomic-embed-text

COPY On-Prem On-Prem

COPY On-Prem/the.conf /etc/nginx/conf.d/the.conf

COPY On-Prem/run.sh /

COPY models On-Prem/upsonic_on_prem/api/utils/ai/

WORKDIR /app/On-Prem

EXPOSE 7340


CMD ["bash", "/run.sh"]
