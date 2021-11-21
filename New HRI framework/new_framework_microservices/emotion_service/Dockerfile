FROM tensorflow/opencv/dlib/py2:latest

RUN mkdir /code

WORKDIR /code

ADD . /code/

RUN apt-get update
RUN echo "Europe/Warsaw" > /etc/timezone &&\
    DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata &&\
    DEBIAN_FRONTEND=noninteractive apt-get install -qq -y python-tk

RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt



EXPOSE 5000

CMD gunicorn -c config.py main:app --log-config gunicorn_log.conf