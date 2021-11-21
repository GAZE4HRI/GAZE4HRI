FROM tensorflow/tensorflow:1.14.0

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -qq -y \
    python-dev python-numpy git make\
    libboost-all-dev wget unzip python-pip
RUN pip install --upgrade pip
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN apt-get install -qq -y build-essential curl cmake libopenblas-dev liblapack-dev
RUN apt-get install -y libsndfile1
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

#type first line befor starting conteiner and second after for pynput working in docker
#xhost +local:root
#xhost -local:root


#example usage
#docker build -t new_fram .
#xhost +local:root
#docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v ${PWD}:/code/ -it new_fram /bin/bash
##root> python runner.py
#xhost -local:root