import qi
import argparse
import sys
import numpy

import vision_definitions
import cv2

class NaoVideoSourceRemote():

    def __init__(self, session):
        self.vd_proxy = session.service("ALVideoDevice")
        self.resolution = vision_definitions.kQVGA
        self.colorSpace = vision_definitions.kYuvColorSpace
        self.fps = 10
        self.nameId = None

    def subscribeCamera(self):
        #subscribe or subscribeCamera?? - subscribe is deprecated
        self.nameId = self.vd_proxy.subscribeCamera("python_GVM", 2, self.resolution, self.colorSpace, self.fps)
        # self.nameId = self.vd_proxy.subscribe("python_GVM7", self.resolution, self.colorSpace, self.fps)

    def getImage(self):
        image = self.vd_proxy.getImageRemote(self.nameId)
        image_width = image[0]
        image_height = image[1]

        return numpy.frombuffer(image[6], numpy.uint8).reshape(image_height, image_width, 1)

    def releaseImage(self):
        self.vd_proxy.releaseImage(self.nameId)

    def unsubscribe(self):
        self.vd_proxy.unsubscribe(self.nameId)



def main(session):
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter("results/test_depth.avi", fourcc, 10.0, (320, 240), 0)
    videoSource = NaoVideoSourceRemote(session)
    videoSource.subscribeCamera()
    for i in range(100):
        img = videoSource.getImage()
        videoSource.releaseImage()
        out.write(img)
        cv2.imwrite("results/test" + str(i) + ".png", img)


    videoSource.unsubscribe()
    out.release()
    cv2.destroyAllWindows()




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.1.101",
                        help="Robot IP address. On robot or Local Naoqi: use '192.168.1.101'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session)