# It is repository of HRI framework server currently under development

## Installation instructions 
there ara 3 ways to start this application, direct, docker, and vm.
All of them require first to run mqtt broker(eg. mosquitto) somewhere, preferably in local network (all data is going through it). 
robot or android app also should be connected before starting server.
### direct
works for linux (windows probably also but installing librarys is problematic and un recommended),
just download repository and type 
~~~
pip inatall -r requirements.txt
~~~    

python 2.7 only

### docker

Works for linux and windows(with small limitation)
run in repository folder
linux commands
~~~
docker build -t new_fram .
xhost +local:root
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v ${PWD}:/code/ -it new_fram /bin/bash
xhost -local:root
~~~

for windows 
~~~
docker build -t new_fram .
docker run  -v ${PWD}:/code/ -it new_fram /bin/bash
~~~
mose (onclick) functionality need to be removed from scenario file to start it up.


### vm
#### Vbox
https://drive.google.com/file/d/1gW3N3zJbaQBN93sUyGQsgfhhpvQp27-Q/view?usp=sharing

it is ubuntu machine with all librarys installed

####Vmware
https://drive.google.com/file/d/1p_ZE7qFPwMSGW1TnpWtR2BVlTksfF9_X/view?usp=sharing

it is packed up folder with vmware wirtual mashine it need to be unpacked in vmware player virtual mashine folder (on Windows default in \Documents\Virtual Machines). It is ubuntu mashine with all needed librarys.

## Starting system ans configuration

System uses python2.7 
to start use 
~~~
python runner.py
~~~

If robot/avatar application is connected to mqtt broker, scenario should start.
Broker ip for this module can be set in runner.py or in config/platform in appropriate file.
Scenario are defined in scenarios/scenarioFiles/ in json file, there can be multiple scenarios in one file eg. interwiew_demo.json one to start is set in line 11 by setting variable corresponding to scenario name to true
Creating new scenario can be chalenge at first but is quite simple after a while and can be simplified by creating gui in future 
