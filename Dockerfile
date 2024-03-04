FROM ubuntu

LABEL org.opencontainers.image.source https://github.com/Upsonic/On-Prem

RUN mkdir /app

RUN apt-get update
RUN apt-get install python3 python3-pip -y
RUN apt-get install nginx redis-server -y
RUN apt-get install openssl -y
RUN apt-get install git-lfs -y
RUN apt-get install curl -y
RUN curl -fsSL https://ollama.com/install.sh | sh
WORKDIR /app/

COPY On-Prem/requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt



COPY On-Prem On-Prem

COPY On-Prem/the.conf /etc/nginx/conf.d/the.conf

COPY On-Prem/run.sh /

COPY models On-Prem/upsonic_on_prem/utils/ai/models

WORKDIR /app/On-Prem

EXPOSE 5000


CMD ["bash", "/run.sh"]
