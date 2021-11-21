import csv
from episode_mining.winepi import WINEPI
from itertools import product

import string
import itertools
import numpy as np

PERIOD = 5.0
FILE = 'contact-aversionTotals.csv'
treshold = 0.1
treshold2 = 1.15





def generate_strings(length=3,chars = "ac"):
    return [''.join(x) for x in itertools.product(chars, repeat=length)]


def generate_strings_to_len(lenght = 5, chars = "ac"):
    res = []
    for i in range(1,lenght):
        res = np.concatenate((res,generate_strings(i,chars)))
    return res

def strict_period():
    dict = {}
    with open(FILE) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(spamreader, None)
        curr_usr = "1"
        temp = []
        curr_time = 0
        aversion = "c"
        counter = 1
        for row in spamreader:
            if not curr_usr == row[2]:
                curr_usr = row[2]
                dict[curr_usr] = temp
                temp = []
            if row[2] == "":
                continue
            curr_time += int(row[3])
            if row[6] == "0":
                aversion = "a"
            if curr_time > PERIOD * 1000:
                temp.append(aversion)
                curr_time = curr_time - (PERIOD * 1000)
                aversion = "c"
        sequence = []
        for v in dict.values():
            for e in v:
                sequence.append((counter,e))
                counter += 1
        chars = "ac"
        episodes = sorted(generate_strings_to_len(6,chars))
        w = WINEPI(sequence, episodes, 'serial')
        print(sequence)
        frq = w.discover_frequent_episodes(1, counter, 5, 0.01)
        for e in frq:
            print(e)
        rules = w.generate_rules(1, counter, 5, 0.01, 0.01)
        for r in rules:
            print(r)

def aversion_direction_strict_period():
    dict = {}
    with open(FILE) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(spamreader, None)
        curr_usr = "1"
        temp = []
        avg = []
        curr_time = 0
        aversion = [0.0,0.0,"1"]
        for row in spamreader:
            # print("{0} {1} {2}".format(row[2], row[3],row[6]))
            if not curr_usr == row[2]:
                mean = np.average(avg, axis=0)
                t = []
                for i in temp:
                    res = "c"
                    if i[2] == "0":
                        diff = [np.abs(a - b) for a, b in zip(i[0:2], mean)]
                        # if np.abs((diff[0] / mean[0]) - (diff[1] / mean[1])) < treshold:
                        if (np.abs(((diff[0] + mean[0]) / mean[0]) - ((diff[1] + mean[1]) / mean[1])) < treshold) or \
                                (((diff[0] + mean[0]) / mean[0]) > treshold2 and (
                                    ((diff[1] + mean[1]) / mean[1]) > treshold2)):
                            res = "f"
                        elif diff[0] - diff[1] > 0:
                            if i[0] < mean[0]:
                                res = "l"
                            if i[0] > mean[0]:
                                res = "r"
                        else:
                            if i[1] < mean[1]:
                                res = "u"
                            if i[1] > mean[1]:
                                res = "d"
                    t.append(res)
                dict[curr_usr] = t
                curr_usr = row[2]
                temp = []
                avg = []
            if row[2] == "":
                continue
            curr_time += int(row[3])

            if row[6] == "1":
                avg.append([float(row[4].replace(",", ".")), float(row[5].replace(",", "."))])

            if row[6] == "0":
                aversion = [float(row[4].replace(",", ".")), float(row[5].replace(",", ".")), row[6]]
            if curr_time > PERIOD * 1000:
                temp.append(aversion)
                curr_time = curr_time - (PERIOD * 1000)
                aversion = [0.0,0.0,"1"]
    counter = 1
    sequence = []
    for v in dict.values():
        for e in v:
            sequence.append((counter, e))
            counter += 1
    chars = "aclrudf"
    episodes = sorted(generate_strings_to_len(6, chars))
    w = WINEPI(sequence, episodes, 'serial')
    print(sequence)
    frq = w.discover_frequent_episodes(1, counter, 7, 0.1)
    for e in frq:
        print(e)
    rules = w.generate_rules(1, counter, 5, 0.1, 0.1)
    for r in rules:
        print(r)

    # for i in ps.frequent(2):
    #     print(i)
    print("\n\n\n")




if __name__ == '__main__':
    # strict_period()
    aversion_direction_strict_period()