FROM ubuntu:18.04


ARG DEBIAN_FRONTEND=noninteractive

ARG BUILD_DIR=/home/build-dep

ARG OPENFACE_DIR=/home/openface-build

RUN mkdir ${OPENFACE_DIR}

RUN mkdir ${BUILD_DIR}



RUN apt-get update && apt-get install -qq -y \
    curl build-essential llvm clang-3.7 libc++-dev \
    libc++abi-dev cmake libopenblas-dev liblapack-dev git libgtk2.0-dev \
    pkg-config libavcodec-dev libavformat-dev libswscale-dev \
    python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libx264-dev \
    libpng-dev libtiff-dev libdc1394-22-dev checkinstall \
    libboost-all-dev wget unzip python-pip 

RUN pip install --upgrade pip 
RUN pip install numpy

ADD https://github.com/opencv/opencv/archive/3.3.0.zip ${BUILD_DIR}

RUN cd ${BUILD_DIR} && unzip 3.3.0.zip && \
    cd opencv-3.3.0 && \
    mkdir -p build && \
    cd build && \
    cmake \
    -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D WITH_FFMPEG=NO \
    -D WITH_IPP=NO \
    -D WITH_OPENEXR=NO \
    -D WITH_TBB=YES \
    -D BUILD_EXAMPLES=NO \
    -D BUILD_ANDROID_EXAMPLES=NO \
    -D INSTALL_PYTHON_EXAMPLES=NO \
    -D BUILD_DOCS=NO \
    -D BUILD_opencv_python2=ON \
    -D BUILD_opencv_python3=NO \
    .. && \
    make VERBOSE=1 && \
    make -j8 && \
    make install 

ADD http://dlib.net/files/dlib-19.13.tar.bz2 ${BUILD_DIR}

RUN cd ${BUILD_DIR} && tar xf dlib-19.13.tar.bz2 && \
    rm -rf dlib-19.13.tar.bz2 && \
    cd dlib-19.13 && \
    mkdir build && \
    cd build && \
    cmake .. && \
    cmake --build . --config Release && \
    make install && \
    ldconfig

RUN cd ${BUILD_DIR}/dlib-19.13 && \
    python setup.py install

ADD https://github.com/l0rd11/OpenFace/archive/newer_boost.zip ${OPENFACE_DIR}

RUN cd ${OPENFACE_DIR} && unzip newer_boost.zip && \
    rm -rf newer_boost.zip  && \
    cd ${OPENFACE_DIR}/OpenFace-newer_boost && mkdir -p build && cd build && \
    cmake  -D CMAKE_BUILD_TYPE=RELEASE CMAKE_CXX_FLAGS="-std=c++11" -D CMAKE_EXE_LINKER_FLAGS="-std=c++11" .. && \
    make 


RUN ln /dev/null /dev/raw1394


