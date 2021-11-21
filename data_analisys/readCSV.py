import csv


import csv

from pyprefixspan import pyprefixspan

from PSpan import PrefixSpan

PERIOD = 5.0
FILE = 'contact-aversionTotals.csv'
treshold = 0.1
treshold2 = 1.15






def read():
    dict = {}
    with open(FILE) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(spamreader, None)
        curr_usr = "1"
        temp = []
        curr_time = 0
        aversion = "1"
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
                aversion = "0"
            if curr_time > PERIOD * 1000:
                temp.append(aversion)
                curr_time = curr_time - (PERIOD * 1000)
                aversion = "1"

    for i in dict.values():
        print(" ".join(i))


if __name__ == '__main__':
    read()