import qi
import argparse
import sys
import time


def main(session):
    """
    This example uses the getCurrentPosition method.
    """
    # Get the service ALAudioPlayer.

    audio_recorder_service = session.service("ALAudioRecorder")
    print "started "
    #plays a file and get the current position 5 seconds later
    audio_recorder_service.startMicrophonesRecording("/home/nao/test.wav", "wav", 48000, (1,1,1,1))

    time.sleep(3)

    #currentPos should be near 3 secs
    audio_recorder_service.stopMicrophonesRecording()
    print "done "


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