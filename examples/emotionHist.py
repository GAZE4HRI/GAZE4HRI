import matplotlib
from matplotlib import pyplot as plt



def load_data(file_name):
    data = {'neutral': 0, 'sad': 0, 'angry': 0, 'happy': 0, 'surprise': 0, 'disgust': 0, 'fear': 0 }
    f = open(file_name, 'r')
    lines = f.readlines()
    for line in lines:
        data[line.replace('\n', '')] += 1

    return data



if __name__ == '__main__':
    data = load_data("resources/emotion_id2.txt")
    print data
    fig = plt.figure(figsize=(12, 12))
    ax = plt.gca()
    x = [i + .5 for i in range(len(data.keys()))]
    ax.bar(x, data.values(), width=.5)
    ax.set_xticks(x)
    ax.set_xticklabels(data.keys(), rotation=45, fontsize=8)
    ax.set_ylabel('emotions')
    plt.tight_layout()
    plt.savefig('resources/emotionsHistogram.png', dpi=100)