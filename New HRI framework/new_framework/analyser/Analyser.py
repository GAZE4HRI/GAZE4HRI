import threading
from Queue import Queue
from collections import Counter, deque
from threading import Thread, currentThread
import time
import cv2
from analyser.gaze.FaceUtils import Face
from analyser.questionDetection.QuestionDetector import QuestionDetector

from requests_futures.sessions import FuturesSession
from utils.Constants import GazeDirection, EventType, SystemState
from datetime import datetime


class Analyser():
    def __init__(self, session, options):

        self.event_separation = options['event_separation']
        self.userID = options['experimentName']
        self.result_directory = options['directory']
        self.options = options
        self.session = session
        self.period = 0.05
        self.robot_video = self.get_robot_video(session, options["robot_name"])
        self.robot_audio =  self.get_robot_audio(session, options["robot_name"])
        self.speech_recognition = self.get_speech_recognition(session, options["STT"])
        self.current_node = options["current_node"]
        self.emotion_queue = None
        self.gaze_queue = None
        self.video_thread = None
        self.gaze_worker = None
        self.speech_thread = None
        self.emotion_worker = None
        self.gaze_results = deque(maxlen=50)
        self.emotion_results = deque(maxlen=50)
        self.emotion_results_full = deque(maxlen=50)
        self.gaze_dir = GazeDirection.LOOKING_ON_ROBOT_FACE
        self.last_gaze_dirs = deque(maxlen=50)
        self.last_emotions = deque(maxlen=50)
        self.emotion = "neutral"
        self.services_address = options["services_address"]
        self.events_to_lissen = []
        self.emotions_lock = threading.Lock()
        self.gaze_dirs_lock = threading.Lock()
        self.question_lock = threading.Lock()
        self.face = Face()
        self.question_detected = False
        self.question_thread = None
        self.question_detector = QuestionDetector(self.robot_audio, self)
        self.question_queue = Queue()
        self.last_question = deque(maxlen=50)
        self.question_results = deque(maxlen=3)
        self.question_results_full = deque(maxlen=3)
        self.question_worker = None
        self.last_event = time.time() + 60
        self.last_event_with_name = {}
        self.silence_detected = False

    def get_current_node(self):
        self.current_node = self.options["current_node"]
        return self.options["current_node"]

    def get_robot_video(self, session, robot_type):
        if robot_type.upper() == "pepper".upper() or robot_type.upper() == "nao".upper():
            from analyser.videoSource.NaoVideoSource import NaoVideoSourceRemote
            return NaoVideoSourceRemote(session)
        elif robot_type.upper() == "avatar".upper():
            from analyser.videoSource.AvatarVideoSource import AvatarVideoSource
            au = self.options.get("AvatarVideoSource", None)
            if au is None:
                au = AvatarVideoSource()
                self.options["AvatarVideoSource"] = au
            return au
        else:
            return False

    def get_robot_audio(self, session, robot_type):
        if robot_type.upper() == "pepper".upper() or robot_type.upper() == "nao".upper():
            from pepper.AvatarAudioSource import AvatarAudioSource
            return AvatarAudioSource(session)
        elif robot_type.upper() == "avatar".upper():
            from analyser.AudioSource.avatarAudioSource import AvatarAudioSource
            au = self.options.get("AvatarAudioSource", None)
            if au is None:
                au = AvatarAudioSource()
                self.options["AvatarAudioSource"] = au
            return au
        else:
            return False

    def get_speech_recognition(self, session, stt):
        if stt.upper() == "google_cloud".upper():
            from analyser.speechRecognition.SpeechRecognition import SpeechRecognition
            return SpeechRecognition(session)
        else:
            return False

    def add_event_to_lissen(self, event_data):
        self.events_to_lissen.append(event_data)
        if event_data['type'] == EventType.SILENCE_DETECTED:
            self.question_detector.silence_treshold = event_data["value"]

    def remove_event_to_lissen(self, event_data):
        self.events_to_lissen.remove(event_data)

    def event(self):
        t = currentThread()
        while getattr(t, "do_run", True):
            now = time.time()
            if not self.options["system_state"][0] == SystemState.IN_BLOCKING_ACTION and time.time() - self.options["system_state"][1] > 5:
                for event_data in self.events_to_lissen:
                    if event_data['type'] == EventType.GAZE_AVERTING:
                        if self.gaze_averting_ocured():
                            if now - self.last_event_with_name.get(event_data['type'], now - event_data['separation'] - 1) < \
                                    event_data['separation']:
                                with self.gaze_dirs_lock:
                                    self.last_gaze_dirs = deque(maxlen=50)
                                continue
                            if now - self.last_event  < self.event_separation:
                                continue
                            self.get_current_node().on_event(event_data)
                            with self.gaze_dirs_lock:
                                self.last_gaze_dirs = deque(maxlen=50)
                            self.last_event = now
                            self.last_event_with_name[event_data['type']] = now

                    if event_data['type'] == EventType.Emotion_OCCURRED:
                        # print "emo" + str(self.emotion_ocured(event_data['value']))
                        if self.emotion_ocured(event_data['value']):
                            if now - self.last_event_with_name.get(event_data['type'], now - event_data['separation'] - 1) < event_data['separation']:
                                with self.emotions_lock:
                                    self.last_emotions = deque(maxlen=50)
                                continue
                            if now - self.last_event < self.event_separation:
                                continue
                            self.get_current_node().on_event(event_data)
                            with self.emotions_lock:
                                self.last_emotions = deque(maxlen=50)
                            self.last_event = now
                            self.last_event_with_name[event_data['type']] = now

                    if event_data['type'] == EventType.QUESTION_DETECTED:
                        if self.question_detected:
                            if now - self.last_event_with_name.get(event_data['type'], now - event_data['separation'] - 1)  < event_data['separation']:
                                with self.question_lock:
                                    self.question_results = deque(maxlen=3)
                                continue
                            if now - self.last_event < self.event_separation:
                                continue
                            self.get_current_node().on_event(event_data)
                            self.question_detected = False
                            with self.question_lock:
                                self.question_results = deque(maxlen=3)
                            self.last_event = now
                            self.last_event_with_name[event_data['type']] = now

                    if event_data['type'] == EventType.SILENCE_DETECTED:
                        if self.silence_detected:
                            if now - self.last_event_with_name.get(event_data['type'], now - event_data['separation'] - 1)  < event_data['separation']:
                                continue
                            if now - self.last_event < self.event_separation:
                                continue
                            print "silence"
                            self.get_current_node().on_event(event_data)
                            self.silence_detected = False
                            self.last_event_with_name[event_data['type']] = now

            time.sleep(0.1)

    def gaze_averting_ocured(self):
        counter = Counter()
        if len(self.last_gaze_dirs) < 30:
            return False
        with self.gaze_dirs_lock:
            for res in self.last_gaze_dirs:
                if res:
                    counter[res] += 1

        if not counter:
            return False
        elif counter.get(GazeDirection.LOOKING_ON_MIDDLE_MIDDLE) in counter.most_common(3) or \
                        counter.get(GazeDirection.LOOKING_ON_ROBOT_FACE) in counter.most_common(3):
            return False
        else:
            return True

    def emotion_ocured(self, emotion):
        counter = Counter()
        if len(self.last_emotions) < 40:
            return False
        with self.emotions_lock:
            for res in self.last_emotions:
                if res:
                    counter[res] += 1

        if not counter:
            return False
        elif (emotion, counter.get(emotion)) in counter.most_common(3):
            return True
        else:
            return False

    def perform_statistic_analisis(self, results):
        counter = Counter()
        for res in results:
            if res:
                counter[res] += 1

        if not counter:
            return None
        else:
            return counter.most_common(1)[0]

    def start_video_analysis(self):
        self.robot_video.subscribeCamera()
        self.gaze_queue = Queue()
        self.emotion_queue = Queue()
        self.video_thread = Thread(target=self.run_video_analysis,
                                   args=())

        self.video_thread.start()
        self.gaze_worker = Thread(target=self.run_gaze_worker, args=())
        self.gaze_worker.start()
        self.emotion_worker = Thread(target=self.run_emotion_worker, args=())
        self.emotion_worker.start()
        self.event_worker = Thread(target=self.event, args=())
        self.event_worker.start()

    def start_speeach_recognicion(self):
        self.speech_thread = Thread(target=self.speech_recognition.run,
                                    args=("test",))
        self.speech_thread.start()

    def stop_speeach_recognicion(self):
        self.speech_thread.do_run = False
        self.speech_thread.join()

    def start_question_detection(self):
        self.question_thread = Thread(target=self.question_detector.run,
                                      args=())
        self.question_thread.start()
        self.question_worker = Thread(target=self.run_question_worker, args=())
        self.question_worker.start()

    def stop_question_detection(self):
        self.question_thread.do_run = False
        self.question_thread.join()

    def stop_video_analysis(self):
        self.video_thread.do_run = False
        self.video_thread.join()
        self.event_worker.do_run = False
        self.event_worker.join()

    def do_save_response_gaze_data(self, response, *args, **kwargs):
        j = response.json()
        if j == None or j == ():
            return
        e = (float(j[0]), float(j[1]))
        self.gaze_queue.put(e)

    def do_save_response_emotion_data(self, response, *args, **kwargs):
        j = response.json()
        if j == None or j == ():
            return
        e = (str(j[0]), float(j[1]))
        self.emotion_queue.put(e)

    def run_question_worker(self):
        file = open(self.result_directory + '/questions.txt', 'w')
        while True:
            item = self.question_queue.get()
            if item is None or item == ():
                break


            with self.question_lock:
                self.question_results_full.append(item)
                self.question_results.append(item[0])
                question = self.perform_statistic_analisis(self.question_results)
            print "question " + str(question)
            file.write(str(question) + ', ' + str(datetime.fromtimestamp(time.time())) + "\n")
            file.flush()
            if question is not None:
                self.question = question[0]
                if question[0] == "questions":
                    self.question_detected = True
                with self.question_lock:
                    self.last_question.append(question)
            self.question_queue.task_done()
        file.close()

    def run_gaze_worker(self):
        file = open(self.result_directory + '/gaze.txt', 'w')
        while True:
            item = self.gaze_queue.get()
            if item is None or item == ():
                break
            self.gaze_results.append(self.gaze_discretization(item[0], item[1]))

            gaze = self.perform_statistic_analisis(self.gaze_results)
            if gaze is not None:
                self.gaze_dir = gaze
                print "gaze " + str(gaze)
                file.write(str(gaze) + ', ' + str(datetime.fromtimestamp(time.time())) + "\n")
                file.flush()
                with self.gaze_dirs_lock:
                    self.last_gaze_dirs.append(gaze)
            self.gaze_queue.task_done()
        file.close()

    def run_emotion_worker(self):

        file = open(self.result_directory + '/emotions.txt','w')
        while True:
            item = self.emotion_queue.get()
            if item is None or item == ():
                break
            self.emotion_results_full.append(item)
            # print item

            self.emotion_results.append(item[0])
            em = self.perform_statistic_analisis(self.emotion_results)
            print "emotion " + str(em)
            file.write(str(em[0]) + ', ' + str(datetime.fromtimestamp(time.time())) + "\n")
            file.flush()
            # print em
            if em is not None:
                self.emotion = em[0]
                with self.emotions_lock:
                    self.last_emotions.append(em[0])
            self.emotion_queue.task_done()
        file.close()

    def run_video_analysis(self):
        """
        Loop on, wait for events until manual interruption.
        """
        print "Starting Gaze Analysis"
        # num = int(waitTime / self.period)
        t = currentThread()
        session = FuturesSession(max_workers=10)
        counter = 0
        while getattr(t, "do_run", True):
            try:
                frame = self.robot_video.getImage()
                self.robot_video.releaseImage()

                f = self.face.find_faces(frame)
                if len(f) == 0:
                    continue
                f = f[0]
                # print frame.shape
                border = 30
                top = f.top() - border if f.top() - border > 0 else 0
                bottom = f.bottom() + border if f.bottom() + border < frame.shape[0] else frame.shape[0]
                left = f.left() - border if f.left() - border > 0 else 0
                right = f.right() + border if f.right() + border < frame.shape[1] else frame.shape[1]

                face_img = frame[top:bottom, left:right]
                # _, img_encoded = cv2.imencode('.jpg', frame)
                _, img_encoded = cv2.imencode('.jpg', face_img)
                content_type = 'image/jpeg'
                headers = {'content-type': content_type}
                # cv2.imwrite("test/face_" + str(counter) + ".png", face_img)
                counter += 1

                f = session.post(self.services_address + "/gaze/gaze", data=img_encoded.tostring(),
                                 headers=headers,
                                 hooks={'response': self.do_save_response_gaze_data})

                f = session.post(self.services_address + "/emotions", data=img_encoded.tostring(), headers=headers,
                                 hooks={'response': self.do_save_response_emotion_data})


            except Exception as e:
                print(type(e))  # the exception instance
                print(e.args)  # arguments stored in .args
                print(e)
                print "Analyser couldn't perform gaze analysis sorry, please contact administrator"

            time.sleep(self.period)
        self.emotion_queue.put(None)
        self.gaze_queue.put(None)

    def gaze_discretization(self, yaw, pitch):
        result = ()
        if -5 <= yaw <= 5:
            if -5 <= pitch <= 5:
                result = GazeDirection.LOOKING_ON_ROBOT_FACE

        if -90 <= yaw <= -10:
            if -90 <= pitch <= -10:
                result = GazeDirection.LOOKING_ON_LEFT_DOWN
        if 10 <= yaw <= 90:
            if -90 <= pitch <= -10:
                result = GazeDirection.LOOKING_ON_RIGHT_DOWN
        if -10 <= yaw <= 10:
            if -90 <= pitch <= -10:
                result = GazeDirection.LOOKING_ON_MIDDLE_DOWN

        if -90 <= yaw <= -10:
            if -10 <= pitch <= 10:
                result = GazeDirection.LOOKING_ON_LEFT_MIDDLE
        if 10 <= yaw <= 90:
            if -10 <= pitch <= 10:
                result = GazeDirection.LOOKING_ON_RIGHT_MIDDLE
        if -10 <= yaw <= 10:
            if -10 <= pitch <= 10:
                result = GazeDirection.LOOKING_ON_MIDDLE_MIDDLE

        if -90 <= yaw <= -10:
            if 10 <= pitch <= 90:
                result = GazeDirection.LOOKING_ON_LEFT_UP
        if 10 <= yaw <= 90:
            if 10 <= pitch <= 90:
                result = GazeDirection.LOOKING_ON_RIGHT_UP
        if -10 <= yaw <= 10:
            if 10 <= pitch <= 90:
                result = GazeDirection.LOOKING_ON_MIDDLE_UP

        # TODO maybe something better
        return result