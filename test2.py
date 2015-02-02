import cPickle as pickle
from collections import OrderedDict


def getTypeIDsFromText():
    typeids_file = open('typeids.txt','r')
    typeids = [line.strip('\n').split('\t') for line in typeids_file.readlines()]
    typeids = [t for t in typeids if len(t)==2]
    typeids = dict(typeids)
    return typeids

def main():
    with open("resultPOI.txt", "r") as result_file:
        profits = pickle.load(result_file)
    print len(profits)
    typeids = getTypeIDsFromText()

    p = [(k,v) for (k,v) in profits.items() if v["INV"]> 100000000 and v["POI"] < 1000]
    sorted_POI = OrderedDict(sorted(p, key=lambda x: x[1]["POI"]))
    POI_index = sorted_POI.keys()
    sorted_INV = OrderedDict(sorted(p, key=lambda x: x[1]["INV"]))
    INV_index = sorted_INV.keys()
    
    tids = dict(p).keys()
    r = {}
    for tid in tids:
        r[tid] = (POI_index.index(tid)+1)*(1+INV_index.index(tid))
    rr = OrderedDict(sorted(r.items(),key=lambda x: x[1]))
    with open("result_sorted_coef.txt", "w") as f:
        for tid in rr:
            print >>f, typeids[tid]
            print >>f, sorted_POI[tid]
            print >>f, rr[tid]
            print >>f, ""

##    with open("result_sorted_POI2.txt", "w") as f:
##        for tid in profits_sorted:
##            print >>f, typeids[tid]
##            print >>f, profits_sorted[tid]
##            print >>f, ""

if __name__=="__main__":
    main()
