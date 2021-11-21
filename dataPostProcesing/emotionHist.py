import csv

import matplotlib
from matplotlib import pyplot as plt

N_EMOTIONS = 3

def load_data(root):
    data = {'neutral': 0., 'sad': 0., 'angry': 0., 'happy': 0., 'surprise': 0., 'disgust': 0., 'fear': 0. }

    with open(root, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            data[row[0].replace('\n', '')] += float(row[1])
    return data

def load_data_bin(root):
    data = {'neutral': 0., 'sad': 0., 'angry': 0., 'happy': 0., 'surprise': 0., 'disgust': 0., 'fear': 0. }

    with open(root, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            data[row[0].replace('\n', '')] += 1.0
    return data

def load_n_data(root, n):
    data = {'neutral': 0., 'sad': 0., 'angry': 0., 'happy': 0., 'surprise': 0., 'disgust': 0., 'fear': 0. }

    with open(root, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            for i in range(n):
                data[row[i].replace('\n', '')] += float(row[i + n])
    return data


def emotion_hist(root, result, n):
    data = load_n_data(root, n)
    print data
    fig = plt.figure(figsize=(12, 12))
    ax = plt.gca()
    x = [i + .5 for i in range(len(data.keys()))]
    ax.bar(x, data.values(), width=.5)
    ax.set_xticks(x)
    ax.set_xticklabels(data.keys(), rotation=45, fontsize=8)
    ax.set_ylabel('emotions')
    plt.tight_layout()
    plt.savefig(result, dpi=300)


data_files = [
    "results/emotions_per_strategy/human_3.txt",
    "results/emotions_per_strategy/aversion_3.txt",
    "results/emotions_per_strategy/contact_3.txt"
]

def normalize(d, target=1.0):
   raw = sum(d.values())
   factor = target/raw
   return {key:value*factor for key,value in d.iteritems()}

def make_chart():
    plt.figure(figsize=(12, 12))

    for i, file in enumerate(data_files):
        data = load_n_data(file, N_EMOTIONS)
        # data.pop("disgust")
        # data.pop("fear")
        data = normalize(data)
        print data

        plt.subplot(131 + i)
        ax = plt.gca()
        x = [i + .5 for i in range(len(data.keys()))]
        ax.bar(x, data.values(), width=.5)
        ax.set_xticks(x)
        ax.set_xticklabels(data.keys(), rotation=45, fontsize=8)
        ax.set_ylabel(file.split('/')[-1][:-4])
        ax.set_ylim((0, 0.6))
    plt.tight_layout()
    plt.savefig('results/emotions_per_strategy/top3.png', dpi=300)

if __name__ == '__main__':
    make_chart()
    # data = load_data("results/emotions_per_strategy/human.txt")
    # print data
    # fig = plt.figure(figsize=(12, 12))
    # ax = plt.gca()
    # x = [i + .5 for i in range(len(data.keys()))]
    # ax.bar(x, data.values(), width=.5)
    # ax.set_xticks(x)
    # ax.set_xticklabels(data.keys(), rotation=45, fontsize=8)
    # ax.set_ylabel('emotions')
    # ax.set_ylim((0, 6000))
    # plt.tight_layout()
    # plt.savefig('results/emotions_per_strategy/human.png', dpi=100)