# HOW to install
## on pepper
befor install
if runinng
```
qicli call ALServiceManager.stopService depthcamera
```
check if is runing
```
qicli call ALServiceManager.services
```
## in project
package
```
qipkg make-package grant_robot.pml 
```
install
```
qipkg deploy-package grant_robot-0.0.2.pkg --url nao@192.168.1.101
```

# more info

http://doc.aldebaran.com/2-5/dev/tutos/create_a_new_service.html

https://github.com/aldebaran/robot-jumpstarter