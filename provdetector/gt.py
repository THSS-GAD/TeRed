if __name__ == '__main__':
    with open('dataset/APT-1(Community)/abnormal-v3-gt-csnap.txt', 'r') as i, open('dataset/APT-1(Community)/abnormal-v3-gt.txt', 'w') as o, open('dataset/APT-1(Community)/abnormal-v3-gt-apache.txt', 'r') as a:
        t = set([f.split('_')[1] for f in i.readlines() if f != '\n'])
        a = set([(f.split('_')[1]).split('.')[0] for f in a.readlines() if f != '\n'])
        for l in t.intersection(a):
            print(l)
        o.writelines([f+'\n' for f in t])