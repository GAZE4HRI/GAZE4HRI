import io
import re
import sys
from threading import currentThread, Thread


import time
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

from pepper.AvatarAudioSource import AvatarAudioSource


class SpeechRecognition(object):
    RATE = 16000
    def __init__(self, session):
        self.language_code = 'pl-PL'

        self.client = speech.SpeechClient()
        self.config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.RATE,
            language_code=self.language_code)
        self.streaming_config = types.StreamingRecognitionConfig(
            config=self.config,
            interim_results=True)
        self.session = session


    def run(self, name):
          # a BCP-47 language tag
        file = io.open(name, 'w')

        with AvatarAudioSource(self.session) as stream:
            audio_generator = stream.generator()

            requests = (types.StreamingRecognizeRequest(audio_content=content.tobytes())
                        for content in audio_generator)

            responses = self.client.streaming_recognize(self.streaming_config, requests)

            # Now, put the transcription responses to use.
            self.listen_print_loop(responses, stream, file)



    def listen_print_loop(self, responses, mod, file):
        """Iterates through server responses and prints them.

        The responses passed is a generator that will block until a response
        is provided by the server.

        Each response may contain multiple results, and each result may contain
        multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
        print only the transcription for the top alternative of the top result.

        In this case, responses are provided for interim results as well. If the
        response is an interim one, print a line feed at the end of it, to allow
        the next result to overwrite it, until the response is a final one. For the
        final one, print a newline to preserve the finalized transcription.
        """
        num_chars_printed = 0
        counter = 0
        for response in responses:
            t = currentThread()
            if not getattr(t, "do_run", True):
                counter = counter + 1
                if counter >= 5:
                    mod.isProcessingDone = True
                    break
            if not response.results:
                continue

            # The `results` list is consecutive. For streaming, we only care about
            # the first result being considered, since once it's `is_final`, it
            # moves on to considering the next utterance.
            result = response.results[0]
            if not result.alternatives:
                continue

            # Display the transcription of the top alternative.
            transcript = result.alternatives[0].transcript

            # Display interim results, but with a carriage return at the end of the
            # line, so subsequent lines will overwrite them.
            #
            # If the previous result was longer than this one, we need to print
            # some extra spaces to overwrite the previous result
            overwrite_chars = ' ' * (num_chars_printed - len(transcript))

            if not result.is_final:
                sys.stdout.write(transcript + overwrite_chars + '\r')
                sys.stdout.flush()
                file.write(transcript + overwrite_chars + '\r')
                file.flush()
                num_chars_printed = len(transcript)

            else:
                print(transcript + overwrite_chars)
                file.write(transcript)
                file.flush()
                # Exit recognition if any of the transcribed phrases could be
                # one of our keywords.
                if re.search(r'\b(exit|quit)\b', transcript, re.I):
                    print('Exiting..')
                    mod.isProcessingDone = True
                    break

                num_chars_printed = 0

if __name__ == '__main__':
    import qi
    session = qi.Session()
    ip = '192.168.1.100'
    port = '9559'
    try:
        session.connect("tcp://" + ip + ":" + port)
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + ip + "\" on port " + port + ".\n"
                                                                               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    g = SpeechRecognition(session)
    threadRecognition = Thread(target=g.run,
                               args=("test.txt",))
    threadRecognition.start()
    time.sleep(20)
    threadRecognition.do_run = False
    threadRecognition.join()
    # g.run("test.txt")