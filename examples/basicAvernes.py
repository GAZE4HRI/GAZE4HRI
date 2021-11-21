#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Use startAwareness and stopAwareness Methods"""

import qi
import argparse
import sys
import time


def main(session):
    """
    This example uses the setEnabled method.
    """
    # Get the services ALBasicAwareness and ALMotion.

    ba_service = session.service("ALBasicAwareness")
    # motion_service = session.service("ALMotion")

    # print "Waiting for the robot to be in wake up position"
    # # motion_service.wakeUp()
    #
    # print "Starting BasicAwareness"
    ba_service.setEnabled(True)
    ba_service.setTrackingMode("Head")
    ba_service.setEngagementMode("FullyEngaged")
    # self.ba_service.setEngagementMode("SemiEngaged")
    ba_service.setStimulusDetectionEnabled("People", True)
    ba_service.setStimulusDetectionEnabled("Sound", True)
    ba_service.setStimulusDetectionEnabled("Movement", False)
    ba_service.setStimulusDetectionEnabled("NavigationMotion", False)
    #
    # print ba_service.setTrackingMode("Head")
    # print "Take some time to play with the robot"
    time.sleep(30)

    print "Stopping BasicAwareness"
    ba_service.setEnabled(False)

    print "Waiting for the robot to be in rest position"
    # motion_service.rest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.1.101",
                        help="Robot IP address. On robot or Local Naoqi: \
                        use '192.168.1.101'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " +
               str(args.port) + ".\n"
               "Please check your script arguments. Run with -h option for \
help.")
        sys.exit(1)

    main(session)
