import cPickle as pickle

with open("result.txt", "r") as result_file:
    z = pickle.load(result_file)

typeids_file = open('typeids.txt','r')
typeids = [line.strip('\n').split('\t') for line in typeids_file.readlines()]
typeids = [t for t in typeids if len(t)==2]
typeids = dict(typeids)

for zz in z:
    print typeids[zz], z[zz]

