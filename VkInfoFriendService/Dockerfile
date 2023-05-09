FROM python:3.8.10-slim

RUN mkdir vkfriends
WORKDIR vkfriends

ADD requirements.txt /vkfriends/
RUN pip install -r requirements.txt
ADD . /vkfriends/

ENV APP_NAME=vkfriends

RUN pip3 install -r requirements.txt


CMD gunicorn vkfriends.wsgi:application -b 0.0.0.0:8000