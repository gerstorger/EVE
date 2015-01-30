import cPickle as pickle

with open("result2.txt", "r") as result_file:
    profit = pickle.load(result_file)

typeids_file = open('typeids.txt','r')
typeids = [line.strip('\n').split('\t') for line in typeids_file.readlines()]
typeids = [t for t in typeids if len(t)==2]
typeids = dict(typeids)

for p in profit:
    print typeids[p], "%.2f" % profit[p]


