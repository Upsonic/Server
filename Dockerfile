FROM ubuntu

LABEL org.opencontainers.image.source https://github.com/Upsonic/On-Prem

RUN mkdir /app

RUN apt-get update
RUN apt-get install python3 python3-pip -y
RUN apt-get install nginx redis-server -y
RUN apt-get install openssl -y
WORKDIR /app/

COPY On-Prem On-Prem
COPY On-Prem/the.conf /etc/nginx/conf.d/the.conf

COPY On-Prem/run.sh /

WORKDIR /app/On-Prem
RUN pip3 install .

EXPOSE 5000


CMD ["bash", "/run.sh"]
