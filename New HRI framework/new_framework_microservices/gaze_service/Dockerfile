FROM ubuntu/opencv/openface:latest
RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN apt-get update
RUN echo "Europe/Warsaw" > /etc/timezone &&\
    DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata &&\
    DEBIAN_FRONTEND=noninteractive apt-get install -qq -y python-tk

RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt &&\
    cp /home/openface-build/OpenFace-newer_boost/build/python/pyopenface.so /code/gaze/pyOpenFace/pyopenface.so

EXPOSE 6000

CMD gunicorn -c config.py gaze_service:app --log-config gunicorn_log.conf