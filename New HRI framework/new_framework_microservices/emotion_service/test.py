import cv2
import requests
import time

def send():
    face = cv2.imread('/home/ja/Dokumenty/Pepper/NewPepperFramework/new_framework_microservices/emotion_service/test.jpg', 3)
    face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    #
    # files = {'file': ('test.jpg',open('test.jpg', 'rb'))}
    # files2 = {'file': ('test.jpg',face.tobytes())}


    # data = open('test.jpg','rb').read()

    _, img_encoded = cv2.imencode('.jpg', face)
    content_type = 'image/jpeg'
    headers = {'content-type': content_type}

    r = requests.post("http://127.0.0.1:8765/emotions",data=img_encoded.tostring(), headers=headers)
    print r.text


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

            r = requests.post("http://127.0.0.1:8765/emotions", data=img_encoded.tostring(), headers=headers)
            print r.text
            print time.time() - time_0

            cv2.imshow('frame', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


if __name__ == "__main__":
    send_video()