import cv2
import requests
import time
import grequests
from requests_futures.sessions import FuturesSession

def send():
    face = cv2.imread('sample1.jpg', 3)
    face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    #
    # files = {'file': ('test.jpg',open('test.jpg', 'rb'))}
    # files2 = {'file': ('test.jpg',face.tobytes())}


    # data = open('test.jpg','rb').read()

    _, img_encoded = cv2.imencode('.jpg', face)
    content_type = 'image/jpeg'
    headers = {'content-type': content_type}
    start = time.time()
    for i in range(20):
        r = requests.post("http://127.0.0.1:6000/gaze",data=img_encoded.tostring(), headers=headers)
        print r.text

    print time.time() - start

def do_something(response, **kwargs):
    print "ser"
    print response.text

def do_something2(response, *args, **kwargs):
    print "ser"
    print response.text

def test_async():
    face = cv2.imread('test.jpg', 3)
    face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    _, img_encoded = cv2.imencode('.jpg', face)
    content_type = 'image/jpeg'
    headers = {'content-type': content_type}
    start = time.time()
    for i in range(20):
        r1 = grequests.post("http://127.0.0.1:6000/gaze", data=img_encoded.tostring(), headers=headers, hooks={'response': do_something})
        grequests.map([r1], size=10)

    print time.time() - start

def test_async2():
    face = cv2.imread('test.jpg', 3)
    face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    face = cv2.resize(face, (640,480))
    print face.shape
    _, img_encoded = cv2.imencode('.jpg', face)
    content_type = 'image/jpeg'
    headers = {'content-type': content_type}
    session = FuturesSession(max_workers=10)
    start = time.time()
    for i in range(20):
        f = session.post("http://127.0.0.1:8765/gaze/gaze", data=img_encoded.tostring(), headers=headers, hooks={'response': do_something2})


    print time.time() - start




def send_video():
    cap = cv2.VideoCapture(
        '/home/ja/Dokumenty/Pepper/dataPostProcesing/resources/try exp/2019-01-1811:01:35.197237id2/videooutput_id2.mp4')
    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:

            img = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            time_0 = time.time()
            _, img_encoded = cv2.imencode('.jpg', img)
            content_type = 'image/jpeg'
            headers = {'content-type': content_type}

            r = requests.post("http://127.0.0.1:6000/gaze", data=img_encoded.tostring(), headers=headers)
            print r.text
            print time.time() - time_0

            cv2.imshow('frame', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


if __name__ == "__main__":
    test_async2()