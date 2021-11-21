import csv

from pyprefixspan import pyprefixspan

from PSpan import PrefixSpan

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
                dict[curr_usr] = [temp]
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

    # for i in list(dict.values()):
    #     print(" ".join(i))
    print(dict.values())

    print("Strict period \n\n")
    model = PrefixSpan.train(list(dict.values()), minSupport=0.5, maxPatternLength=5)
    result = model.freqSequences().collect()
    for fs in result:
        print('{}, {}'.format(fs.sequence, fs.freq))
    print("\n")
    print("\n")

    # for i in ps.frequent(2):
    #     print(i)
    print("\n\n\n")

if __name__ == '__main__':
    strict_period()