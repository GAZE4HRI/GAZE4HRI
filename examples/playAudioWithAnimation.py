
import qi
import argparse
import sys

import time


def main(session):
    """
    This example uses the run method.
    """
    # Get the service ALAnimationPlayer.

    animation_player_service = session.service("ALAnimationPlayer")
    audio_player_service = session.service("ALAudioPlayer")
    audioDeviceService = session.service("ALAudioDevice")

    # play an animation, this will return when the animation is finished
    # animation_player_service.run("animations/Stand/Gestures/Hey_1")

    fileId = audio_player_service.loadFile("/home/nao/experiment-one/audio/sentence4.wav")
    print audioDeviceService.setOutputVolume(95)
    n = audio_player_service.play(fileId, 0.5, 0.0, _async=True)
    # play an animation, this will return right away
    gests = [
             ["animations/Stand/Gestures/Thinking_3",0],
             ["animations/Stand/Gestures/Explain_5",1]
             ]

    for ges in gests:
        future = animation_player_service.run(ges[0], _async=True)
        # wait the end of the animation
        future.value()
        time.sleep(ges[1])



    n.value()
    # # play an animation, this will return right away
    # future = animation_player_service.run("animations/Stand/Gestures/Hey_1", _async=True)
    # # stop the animation
    # future.cancel()


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