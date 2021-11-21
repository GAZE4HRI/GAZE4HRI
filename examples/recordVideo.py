import qi
import argparse
import sys
import time


def main(session):

    videoService = session.service("ALVideoRecorder")
    print "started "
    videoService.setResolution(2)
    # videoService.setCameraID(2)
    videoService.startRecording("/home/nao/", "test.avi", True)
    time.sleep(10)

    videoService.stopRecording()


    print "done "


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