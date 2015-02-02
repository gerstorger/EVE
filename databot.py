import simplejson
import urllib2
import cPickle as pickle
from collections import OrderedDict
from operator import itemgetter
import yaml
from datetime import datetime
import sys

import market


CURRENT_TIME_STRING = str(datetime.now())[:-7]




def getTypeIDsFromText():
    typeids_file = open('typeids.txt','r')
    typeids = [line.strip('\n').split('\t') for line in typeids_file.readlines()]
    typeids = [t for t in typeids if len(t)==2]
    typeids = dict(typeids)
    return typeids

def getTypeIDsFromYAML():
    f = open('typeIDs.yaml','r')
    d = yaml.load(f)
    return d.keys()

def almost_equal(vol_buy, vol_sell):
    return abs(vol_sell-vol_buy) < 0.2*vol_sell and abs(vol_sell-vol_buy) < 0.2*vol_buy

def pickle_dump(obj, filename):
    try:
        with open(filename, "w") as f:
            pickle.dump(obj, f)
    except Exception:
        print "Can't write file", filename  

def pickle_load(filename):
    try:
        with open(filename, "r") as f:
            return pickle.load(f)
    except Exception:
        print "Can't load file", filename

def print_profit(p, fd = sys.stdout):
    print >>fd, p["NAME"]
    print >>fd, "PAT %s" % '{:20,.2f}'.format(p["PAT"])
    print >>fd, "INV %s" % '{:20,.2f}'.format(p["INV"])
    print >>fd, "TOP %s" % '{:20,.2f}'.format(p["TOP"])
    print >>fd, "POI %s" % '{:20,.2f}'.format(p["POI"])
    print >>fd, ""
    
def print_profits(profits, filename = ""):
    if len(filename) == 0:
        f = sys.stdout
    else:
        try:
            f = open(filename,"w")
        except Exception:
            print "Can't open file", filename
            return
    for p in profits:
        print_profit(profits[p], f)
    if len(filename) != 0:
        f.close()
        

def main():
    typeids = getTypeIDsFromText()
    
    profits = {}
    counter=  0 
    for tid in typeids:
        try:
            request = "http://api.eve-central.com/api/marketstat/json?typeid=%s&usesystem=30000142" % tid
            stream = urllib2.urlopen(request).read()
            d = simplejson.loads(stream.strip("]").strip("["))
            sell = d['sell']['wavg']
            buy = d['buy']['wavg']
            vol_sell = d['sell']['volume']
            vol_buy = d['buy']['volume']
            vol_avg = (vol_sell + vol_buy)/2
            if almost_equal(vol_buy, vol_sell):
                profit = market.profit_after_tax(buy,sell,vol_avg)
                if profit > 0:
                    POI = profit / ( vol_avg*buy ) *100
                    tax = market.tax(buy,sell,vol_avg)

                    profits[tid] = {"NAME":typeids[tid], "PAT":profit, "INV":vol_avg*buy, "TOP":tax/profit*100, "POI": POI}
                    print_profit(profits[tid])
                    counter = counter +1
                    if counter == 10:
                        break
                    continue
        except Exception, e:
            print typeids[tid]
            print e
            continue
##    result = OrderedDict(sorted(profits.items(), key=itemgetter(1)))
        
    pickle_dump(profits, CURRENT_TIME_STRING+".bak")

    profits_filtered = ((k,v) for (k,v) in profits.items() if market.good_deal(v["PAT"], v["INV"], v["TOP"], v["POI"]))
    profits_sorted = OrderedDict(sorted(profits_filtered, key=lambda x: market.rank(x[1]["PAT"], x[1]["INV"], x[1]["TOP"], x[1]["POI"])))
    print_profits(profits_sorted, CURRENT_TIME_STRING+".txt")

##    sorted_POI = OrderedDict(sorted(p, key=lambda x: x[1]["POI"]))
##    POI_index = sorted_POI.keys()
##    sorted_INV = OrderedDict(sorted(p, key=lambda x: x[1]["INV"]))
##    INV_index = sorted_INV.keys()
##    
##    tids = dict(p).keys()
##    r = {}
##    for tid in tids:
##        r[tid] = (POI_index.index(tid)+1)*(1+INV_index.index(tid))
##    rr = OrderedDict(sorted(r.items(),key=lambda x: x[1]))
##    with open("result_sorted_coef.txt", "w") as f:
##        for tid in rr:
##            print >>f, typeids[tid]
##            print >>f, sorted_POI[tid]
##            print >>f, rr[tid]
##            print >>f, ""


if __name__ =='__main__':
    main()
