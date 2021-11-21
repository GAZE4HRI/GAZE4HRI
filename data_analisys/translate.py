files = ["results_aversion_direction.txt",
         "results_aversion_direction_one_stacking.txt",
         "results_aversion_direction_strict_adaptive_period.txt",
         "results_aversion_direction_strict_period.txt",
         "results_one_stacking.txt",
         "results_raw_data.txt",
         "results_Strict_adaptive_period.txt",
         "results_Strict_period.txt"]

src_files = ["aversion_direction.txt",
         "aversion_direction_one_stacking.txt",
         "aversion_direction_strict_adaptive_period.txt",
         "aversion_direction_strict_period.txt",
         "one_stacking.txt",
         "raw_data.txt",
         "Strict_adaptive_period.txt",
         "Strict_period.txt"]

files2 = ["results/results_aversion_direction_less_dir.txt"]
src_files2 = ["resources/aversion_direction_less_dirs.txt"]
dic = {"2":"c", "1":"a", "3":"d", "4":"u", "5":"r", "6":"l", "7":"f"}

dic2 = {"2":"c", "1":"a", "3":"v", "4":"h", "5":"f"}

def translate(file, dic):
    f = open(file, "r")
    lines = f.readlines()
    res = []
    for line in lines:
        line = line.replace("-1", "")
        line = line.replace("-2", "")
        for k,v in dic.items():
            line = line.replace(" " + k + " ", " " + v + " ")
            line = line.replace(k + " ",v + " ")
        res.append(line)
    f.close()
    r = open(file.replace(".txt","_trans.txt"), "w")
    r.writelines(res)
    r.close()


def main():
    for file in files2:
        translate(file, dic2)
    for file in src_files2:
        translate(file, dic2)


if __name__ == '__main__':
    main()