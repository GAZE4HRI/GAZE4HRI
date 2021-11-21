#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

import qi
import argparse
import sys



def main(session):
    speech_service = session.service("ALTextToSpeech")
    speech_service.say(" chi mosiesh podach pgick wad demonstroo yont'si tvoye oomeaeyEntnoshch pgiv vood dch'e   ")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
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