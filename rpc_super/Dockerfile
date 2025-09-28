FROM continuumio/miniconda3:22.11.1-alpine

ENV LANG=C.UTF-8 
ENV TZ=Asia/Shanghai

COPY ./.pip/pip.conf /etc/pip.conf
RUN python3 -m pip install --upgrade pip
COPY ./.pip/requirements.txt /usr/src/conf/requirements.txt
RUN pip3 install -r /usr/src/conf/requirements.txt

