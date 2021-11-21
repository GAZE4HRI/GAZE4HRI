import os
human = [

    'wed_3/2019-04-1013:14:07.485439id21/emotions_id21.txt',
    'wed_3/2019-04-1011:53:42.565270id18/emotions_id18.txt',
    'wed_3/2019-04-1010:51:37.495931id15/emotions_id15.txt',
    'wed_3/2019-04-1014:40:38.001720id24/emotions_id24.txt',
    'thu_3/2019-04-1114:37:40.296033id33/emotions_id33.txt',
    'thu_3/2019-04-1109:52:24.573185id27/emotions_id27.txt',
    'thu_3/2019-04-1111:47:21.618287id30/emotions_id30.txt',
    'tue_3/2019-04-0910:33:26.405141id3/emotions_id3.txt',
    'tue_3/2019-04-0915:39:28.597260id12/emotions_id12.txt',
    'tue_3/2019-04-0912:03:48.588439id6/emotions_id6.txt',
    'tue_3/2019-04-0913:57:51.998199id9/emotions_id9.txt'
]
aversion = [
    'tue_3/2019-04-0910:23:23.108225id2/emotions_id2.txt',
    'tue_3/2019-04-0911:46:17.785160id5/emotions_id5.txt',
    'tue_3/2019-04-0913:35:10.023485id8/emotions_id8.txt',
    'tue_3/2019-04-0915:01:11.911125id11/emotions_id11.txt',
    'wed_3/2019-04-1010:15:12.779935id14/emotions_id14.txt',
    'wed_3/2019-04-1011:12:12.036243id17/emotions_id17.txt',
    'wed_3/2019-04-1012:57:00.656255id20/emotions_id20.txt',
    'wed_3/2019-04-1014:17:10.200323id23/emotions_id23.txt',
    'wed_3/2019-04-1015:15:44.147436id26/emotions_id26.txt',
    'thu_3/2019-04-1111:34:37.782417id29/emotions_id29.txt',
    'thu_3/2019-04-1114:24:26.842997id32/emotions_id32.txt',
    'thu_3/2019-04-1115:34:59.298714id35/emotions_id35.txt',
    'thu_3/2019-04-1115:49:28.986608id36/emotions_id36.txt',

]
contact = [
    'tue_3/2019-04-0909:58:02.182721id1/emotions_id1.txt',
    'tue_3/2019-04-0910:57:17.065208id4/emotions_id4.txt',
    'tue_3/2019-04-0913:23:04.868088id7/emotions_id7.txt',
    'tue_3/2019-04-0914:40:04.673977id10/emotions_id10.txt',
    'wed_3/2019-04-1010:01:37.897575id13/emotions_id13.txt',
    'wed_3/2019-04-1011:03:06.840903id16/emotions_id16.txt',
    'wed_3/2019-04-1012:22:22.154943id19/emotions_id19.txt',
    'wed_3/2019-04-1014:04:56.687320id22/emotions_id22.txt',
    'wed_3/2019-04-1015:01:07.157790id25/emotions_id25.txt',
    'thu_3/2019-04-1110:45:18.193433id28/emotions_id28.txt',
    'thu_3/2019-04-1113:01:47.621399id31/emotions_id31.txt',
    'thu_3/2019-04-1114:52:29.618650id34/emotions_id34.txt',
]

RESOURCES_ROOT = '/home/ja/Dokumenty/Pepper/dataPostProcesing/results/'

def get_data_Structure(root):
    d = None
    f = []
    for path, dirs, files in os.walk(root):
        if d == None:
            d = dirs
        for fil in files:
            if "emotions" in fil:
                f.append((path.replace(root, '')+ os.sep + fil))

    return f


def merge(dict):
    for name, strategy in dict.iteritems():
        with open("results/emotions_per_strategy/" + name + "_3.txt", "w") as res:
            for file in strategy:
                with open(RESOURCES_ROOT + file, "r") as f:
                    lines = f.readlines()
                    res.writelines(lines)



if __name__ == '__main__':
    # print get_data_Structure(RESOURCES_ROOT)
    merge({"human" : human, "aversion" : aversion, "contact" : contact})