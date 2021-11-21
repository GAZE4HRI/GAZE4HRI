import csv
import os

import errno
import re

import cv2
from ast import literal_eval as make_tuple

from emotionHist import emotion_hist
from emotions.emotions import extract_emotions
from gaze.GazeEstimator import GazeEstimator, transformToDeg
from gaze.pyOpenFace.pyOpenFaceStub import PyOpenFaceStub
from heatMap import make_heat_map
from printGaze import print_gaze

RESULTS_ROOT = 'results/thu_3'
RESOURCES_ROOT = '/home/ja/Dokumenty/Pepper/results/gaze experiment 04.2019/thursday'

# RESULTS_ROOT = 'results/test3'
# RESOURCES_ROOT = 'resources/test'
user_re = re.compile('.*_(.*)\.mp4')
N_EMOTIONS = 3
def get_data_Structure(root):
    d = None
    f = []
    for path, dirs, files in os.walk(root):
        if d == None:
            d = dirs
        for fil in files:
            if "videooutput" in fil:
                f.append((path.replace(root, '').lstrip(os.sep), fil))

    return f, d



def prepare_result_structure(root, dirs):
    for d in dirs:
        directory = root + os.sep + d
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


def run_extraction(resources, results, files):
    result_files = []
    p = PyOpenFaceStub()
    gazeEstimator = GazeEstimator(p)
    for f in files:
        p.reset()
        video_source = resources + os.sep + f[0] + os.sep + f[1]
        user = user_re.match(f[1]).group(1)
        file_name = results + os.sep + f[0] + os.sep + "gaze_" + user + ".txt"
        output_video = results + os.sep + f[0] + os.sep + "emotions_" + user + ".avi"

        output_data = results + os.sep + f[0] + os.sep + "emotions_" + user + ".txt"
        result_files.append((f, file_name, output_data))


        extract_emotions(video_source, output_video, output_data, N_EMOTIONS)
        # extract_gaze(file_name, gazeEstimator, p, video_source)

    return result_files


def extract_gaze(file_name, gazeEstimator, p, video_source):
    res = open(file_name, 'w')
    cap = cv2.VideoCapture(video_source)
    counter = 100
    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            img = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            yaw, pitch = transformToDeg(gazeEstimator.estimate(img))
            print(yaw, pitch)
            res.write("{0} {1}\n".format(yaw, pitch))
            res.flush()
            counter += 1
            if counter >= 100:
                p.reset()
                counter = 0
        else:
            break
    cap.release()
    res.close()





def save_data(root, res):
    with open(root + os.sep + 'results.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for r in res:
            writer.writerow(r)

def load_data(root):
    data = []
    with open(root, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in reader:
            data.append(make_tuple(row[0]))
    return data

def load_results(root):
    data = []
    with open(root, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in reader:
            data.append((make_tuple(row[0]), row[1], row[2]))
    return data

def prepare_data():
    files, dirs = get_data_Structure(RESOURCES_ROOT)
    prepare_result_structure(RESULTS_ROOT, dirs)
    res = run_extraction(RESOURCES_ROOT, RESULTS_ROOT, files)
    save_data(RESULTS_ROOT, res)


def make_heat_maps(root, data):
    for row in data:
        offset = load_data(root + os.sep + row[0][0] + os.sep + 'offset.csv')[0]
        gaze_file = row[1]
        name = root + os.sep + row[0][0] + os.sep + "gazeHeatMap.jpg"
        bacground = "resources/workplace.jpg"
        make_heat_map(gaze_file, name, offset, bacground)

def make_emotion_hist(root, data):
    for row in data:
        emotion_file = row[2]
        name = root + os.sep + row[0][0] + os.sep + "emotionsHist.jpg"
        emotion_hist(emotion_file, name, N_EMOTIONS)


def make_print_gaze(root, resources, data):
    for row in data:
        offset = load_data(root + os.sep + row[0][0] + os.sep + 'offset.csv')[0]
        gaze_file = row[1]
        source_name = resources + os.sep + row[0][0] + os.sep + row[0][1]
        output_name = root + os.sep + row[0][0] + os.sep + "gaze.avi"
        bacground = "resources/workplace.jpg"
        print_gaze(gaze_file, offset, source_name, output_name, bacground)


if __name__ == '__main__':
    prepare_data()
    data = load_results(RESULTS_ROOT + os.sep + 'results.csv')
    # make_heat_maps(RESULTS_ROOT, data)
    # make_print_gaze(RESULTS_ROOT, RESOURCES_ROOT, data)
    make_emotion_hist(RESULTS_ROOT, data)
    # print data