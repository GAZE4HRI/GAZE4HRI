import csv
from prefixspan import PrefixSpan
import numpy as np

PERIOD = 5.0
FILE = 'contact-aversionTotals.csv'
treshold = 0.1
treshold2 = 1.15

def strict_period():
    dict = {}
    with open(FILE) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(spamreader, None)
        curr_usr = "1"
        temp = []
        curr_time = 0
        aversion = "c"
        for row in spamreader:
            # print("{0} {1} {2}".format(row[2], row[3],row[6]))
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

    for i in list(dict.values()):
        print(" -1 ".join(i) + " -2")
    # print(dict.values())
    ps = PrefixSpan(list(dict.values()))
    print("Strict period \n\n")
    ps.minlen = 3
    ps.maxlen = 8
    for i in ps.topk(20 ):
        print(i)
    print("\n")
    for i in ps.topk(20, closed=True):
        print(i)
    print("\n")
    for i in ps.topk(20, generator=True):
        print(i)
    # print("\n")

    # for i in ps.frequent(2):
    #     print(i)
    print("\n\n\n")


def strict_adaptive_period():
    dict = {}
    with open(FILE) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(spamreader, None)
        curr_usr = "1"
        temp = []
        curr_time = 0
        aversion = "c"
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
                temp.append(aversion)
                aversion = "c"
                curr_time = 0

            if curr_time > PERIOD * 1000:
                temp.append(aversion)
                curr_time = curr_time - (PERIOD * 1000)
                aversion = "c"

    for i in list(dict.values()):
        print(" -1 ".join(i) + " -2")
    # print(dict.values())
    ps = PrefixSpan(list(dict.values()))
    print("Strict adaptive period \n\n")
    ps.minlen = 3
    ps.maxlen = 8
    for i in ps.topk(20 ):
        print(i)
    print("\n")
    for i in ps.topk(20, closed=True):
        print(i)
    print("\n")
    for i in ps.topk(20, generator=True):
        print(i)
    print("\n")

    # for i in ps.frequent(2):
    #     print(i)
    print("\n\n\n")


def one_stacking_period():
    dict = {}
    with open(FILE) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(spamreader, None)
        curr_usr = "1"
        temp = []
        curr_time = 0
        aversion = "c"
        for row in spamreader:
            if not curr_usr == row[2]:
                curr_usr = row[2]
                dict[curr_usr] = temp
                temp = []
            if row[2] == "":
                continue


            curr_time += int(row[3])
            if row[6] == "0":
                if aversion == "c":
                    temp.append(aversion)
                aversion = "a"
                temp.append(aversion)
                aversion = "c"
                curr_time = 0

            if curr_time > PERIOD * 1000:
                temp.append(aversion)
                curr_time = curr_time - (PERIOD * 1000)
                aversion = "c"

    for i in list(dict.values()):
        print(" -1 ".join(i) + " -2")
    # print(dict.values())
    ps = PrefixSpan(list(dict.values()))
    print("one stacking period \n\n")
    ps.minlen = 3
    ps.maxlen = 8
    for i in ps.topk(20 ):
        print(i)
    print("\n")
    for i in ps.topk(20, closed=True):
        print(i)
    print("\n")
    for i in ps.topk(20, generator=True):
        print(i)
    print("\n")

    # for i in ps.frequent(2):
    #     print(i)
    print("\n\n\n")


def raw_data():
    dict = {}
    with open(FILE) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(spamreader, None)
        curr_usr = "1"
        temp = []
        for row in spamreader:

            if not curr_usr == row[2]:
                curr_usr = row[2]
                dict[curr_usr] = temp
                temp = []
            if row[2] == "":
                continue
            if row[6] == "0":
                temp.append("a")
            else:
                temp.append("c")


    for i in list(dict.values()):
        print(" -1 ".join(i) + " -2")
    # print(dict.values())
    ps = PrefixSpan(list(dict.values()))
    print("raw data \n\n")
    ps.minlen = 3
    ps.maxlen = 8
    for i in ps.topk(20):
        print(i)
    print("\n")
    for i in ps.topk(20, closed=True):
        print(i)
    print("\n")
    for i in ps.topk(20, generator=True):
        print(i)
    print("\n")
    # for i in ps.frequent(2):
    #     print(i)
    print("\n\n\n")


def aversion_direction():
    dict = {}
    with open(FILE) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(spamreader, None)
        curr_usr = "1"
        temp = []
        avg = []

        for row in spamreader:

            if not curr_usr == row[2]:
                mean = np.average(avg, axis=0)
                t = []
                for i in temp:
                    res = "c"
                    if i[2] == "0":
                        diff = [np.abs(a - b) for a, b in zip(i[0:2], mean)]
                        # if np.abs((diff[0] / mean[0]) - (diff[1] / mean[1])) < treshold:
                        if (np.abs(((diff[0] + mean[0]) / mean[0]) - ((diff[1] + mean[1]) / mean[1])) < treshold) or \
                                (((diff[0] + mean[0]) / mean[0]) > treshold2 and (((diff[1] + mean[1]) / mean[1]) > treshold2)) :
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
            temp.append([float(row[4].replace(",",".")), float(row[5].replace(",",".")), row[6]])
            if row[6] == "1":
                avg.append([float(row[4].replace(",",".")), float(row[5].replace(",","."))])



    for i in list(dict.values()):
        print(" -1 ".join(i) + " -2")
    # print(dict.values())
    ps = PrefixSpan(list(dict.values()))
    print("aversion_direction \n\n")
    ps.minlen = 3
    ps.maxlen = 8
    for i in ps.topk(20):
        print(i)
    print("\n")
    for i in ps.topk(20, closed=True):
        print(i)
    print("\n")
    for i in ps.topk(20, generator=True):
        print(i)
    print("\n")
    # for i in ps.frequent(4, closed=True):
    #     print(i)
    print("\n\n\n")

# d-3 u-4 r-5 l-6 f-7
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

    for i in list(dict.values()):
        print(" -1 ".join(i) + " -2")
    # print(dict.values())
    ps = PrefixSpan(list(dict.values()))
    print("aversion_direction_strict_period \n\n")
    ps.minlen = 3
    ps.maxlen = 8
    for i in ps.topk(20 ):
        print(i)
    print("\n")
    for i in ps.topk(20, closed=True):
        print(i)
    print("\n")
    for i in ps.topk(20, generator=True):
        print(i)
    print("\n")

    # for i in ps.frequent(2):
    #     print(i)
    print("\n\n\n")


def aversion_direction_strict_adaptive_period():
    dict = {}
    with open(FILE) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(spamreader, None)
        curr_usr = "1"
        temp = []
        avg = []
        curr_time = 0
        aversion = [0.0, 0.0, "1"]
        for row in spamreader:
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

            if row[6] == "1":
                avg.append([float(row[4].replace(",", ".")), float(row[5].replace(",", "."))])
            curr_time += int(row[3])
            if row[6] == "0":
                aversion = [float(row[4].replace(",", ".")), float(row[5].replace(",", ".")), row[6]]
                temp.append(aversion)
                aversion = [0.0, 0.0, "1"]
                curr_time = 0

            if curr_time > PERIOD * 1000:
                temp.append(aversion)
                curr_time = curr_time - (PERIOD * 1000)
                aversion = [0.0, 0.0, "1"]

    for i in list(dict.values()):
        print(" -1 ".join(i) + " -2")
    # print(dict.values())
    ps = PrefixSpan(list(dict.values()))
    print("aversion_direction_strict_adaptive_period \n\n")
    ps.minlen = 3
    ps.maxlen = 8
    for i in ps.topk(20 ):
        print(i)
    print("\n")
    for i in ps.topk(20, closed=True):
        print(i)
    print("\n")
    for i in ps.topk(20, generator=True):
        print(i)
    print("\n")

    # for i in ps.frequent(2):
    #     print(i)
    print("\n\n\n")

def aversion_direction_one_stacking_period():
    dict = {}
    with open(FILE) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(spamreader, None)
        curr_usr = "1"
        avg = []
        curr_time = 0
        aversion = [0.0, 0.0, "1"]
        temp = []
        for row in spamreader:
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

            if row[6] == "1":
                avg.append([float(row[4].replace(",", ".")), float(row[5].replace(",", "."))])
            curr_time += int(row[3])
            if row[6] == "0":
                if aversion[2] == "1":
                    temp.append(aversion)
                aversion = [float(row[4].replace(",", ".")), float(row[5].replace(",", ".")), row[6]]
                temp.append(aversion)
                aversion = [0.0, 0.0, "1"]
                curr_time = 0

            if curr_time > PERIOD * 1000:
                temp.append(aversion)
                curr_time = curr_time - (PERIOD * 1000)
                aversion = [0.0, 0.0, "1"]

    for i in list(dict.values()):
        print(" -1 ".join(i) + " -2")
    # print(dict.values())
    ps = PrefixSpan(list(dict.values()))
    print("aversion direction one stacking period \n\n")
    ps.minlen = 3
    ps.maxlen = 8
    for i in ps.topk(20 ):
        print(i)
    print("\n")
    for i in ps.topk(20, closed=True):
        print(i)
    print("\n")
    for i in ps.topk(20, generator=True):
        print(i)
    print("\n")

    # for i in ps.frequent(2):
    #     print(i)
    print("\n\n\n")




def main():
    # strict_period()
    # strict_adaptive_period()
    # raw_data()
    one_stacking_period()
    # aversion_direction()
    # aversion_direction_strict_period()
    # aversion_direction_strict_adaptive_period()
    aversion_direction_one_stacking_period()



if __name__ == '__main__':
    main()