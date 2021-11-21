import qi
import argparse
import sys
import time


def main(session):
    """
    This example uses the getCurrentPosition method.
    """
    # Get the service ALAudioPlayer.

    audio_player_service = session.service("ALAudioPlayer")
    audioDeviceService = session.service("ALAudioDevice")

    #plays a file and get the current position 5 seconds later
    # fileId = audio_player_service.playFile("/home/nao/experiment-one/audio/greating.wav")
    # audio_player_service.play(fileId, _async=True)
    fileId = audio_player_service.loadFile("/home/nao/experiment-one/audio/greating.wav")
    print audioDeviceService.setOutputVolume(95)
    n = audio_player_service.play(fileId, 0.5, 0.0, _async=True)
    print audio_player_service.getMasterVolume()
    time.sleep(3)
    n.value()
    print "ser"
    #currentPos should be near 3 secs
    # currentPos = audio_player_service.getCurrentPosition(fileId)
    # print "The current position in file is: ", currentPos


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.ip + ":" + str(args.port)
        app = qi.Application(["test", "--qi-url=" + connection_url])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) + ".\n"
                                                                                              "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()

    main(app.session)