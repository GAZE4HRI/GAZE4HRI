import almath
import qi
import argparse
import sys
import time


def main(session):

    motion_service  = session.service("ALMotion")
    posture_service = session.service("ALRobotPosture")
    animation_player_service = session.service("ALAnimationPlayer")
    posture_service.goToPosture("Stand", 0.5)

    moveHead(motion_service, (0.0, -10.0))
    time.sleep(4)
    moveHead(motion_service,(0.0,-35.0))
    time.sleep(0.3)
    moveHead(motion_service, (0.0, -10.0))
    # names  = "Body"

    # n = motion_service.getBodyNames("Body")
    #
    # maxSpeedFraction  = 0.1
    #
    # print n
    # print names
    # motion_service.angleInterpolationWithSpeed(['HeadYaw', 'HeadPitch', 'HipPitch', 'KneePitch'],
    #                                            [0.01, -0.285329238474369, -0.45, 0.2],
    #                                            maxSpeedFraction)
    # animation_player_service.run("animations/Stand/Gestures/Hey_3")
    # motion_service.angleInterpolationWithSpeed(['HeadYaw', 'HeadPitch', 'HipPitch', 'KneePitch'],
    #                                            [0.0, -0.285329238474369, -0.3, 0.1],
    #                                            maxSpeedFraction)

def moveHead(motion_service, angles):
        # (-50, 50) degrees
        #           --
        #        -- 00 ++
        #           ++
    if not len(angles) == 2:
        raise ValueError("not enough arguments")
    if angles[0] >= 80 or angles[0] <= -80:
        raise ValueError("Illegal yaw angles value")
    if angles[1] >= 40 or angles[1] <= -40:
        raise ValueError("Illegal pitch angles value")
        # maybe use stiffnessInterpolation?

    names = "Head"

        # self.motion_service.setStiffnesses("Head", 1.0)
    yaw = angles[0] * almath.TO_RAD
    pitch = angles[1] * almath.TO_RAD
    fractionMaxSpeed = 0.8
    motion_service.angleInterpolationWithSpeed(names, [yaw, pitch], fractionMaxSpeed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.1.101",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
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