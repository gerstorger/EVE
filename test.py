import simplejson
import urllib2

import cPickle as pickle
from collections import OrderedDict
from operator import itemgetter
import yaml

def broker_fee (broker_rel, fact_st, corp_st):
    return (1.000 - 0.050 * broker_rel) / 2 ** (0.1400 * fact_st + 0.06000 * corp_st)

BROKER_REL = 5
FACT_ST = 1.5
CORP_ST = 3.5
BROKER_FEE = broker_fee(BROKER_REL, FACT_ST, CORP_ST)/100
SELL_TAX= 0.75/100

def tax (buy, sell, vol, broker_fee = BROKER_FEE, sell_tax=SELL_TAX):
    return vol*(sell*(broker_fee+sell_tax) + buy*broker_fee)
def profit_after_tax (buy, sell, vol, broker_fee = BROKER_FEE, sell_tax=SELL_TAX):
    return vol*(sell - buy) - tax(buy,sell,vol,broker_fee,sell_tax)

def getTypeIDsFromText():
    typeids_file = open('typeids.txt','r')
    typeids = [line.strip('\n').split('\t') for line in typeids_file.readlines()]
    typeids = [t for t in typeids if len(t)==2]
    typeids = dict(typeids)

def getTypeIDsFromYAML():
    f = open('typeIDs.yaml','r')
    d = yaml.load(f)
    return d.keys()

def main():
    typeids = getTypeIDsFromYAML()
    
    profits = {}
    for tid in typeids:
        try:
            request = "http://api.eve-central.com/api/marketstat/json?typeid=%s&usesystem=30000142" % tid
            stream = urllib2.urlopen(request).read()
            d = simplejson.loads(stream.strip("]").strip("["))
            sell = d['sell']['min']
            buy = d['buy']['max']
            vol_sell = d['sell']['volume']
            vol_buy = d['buy']['volume']
            sell = float(sell)
            buy = float(buy)
            vol_sell = float(vol_sell)
            vol_buy = float(vol_buy)
            if abs(vol_sell-vol_buy) < 0.2*vol_sell and abs(vol_sell-vol_buy) < 0.2*vol_buy:
                profit = profit_after_tax(buy,sell,(vol_sell+vol_buy)/2/10)
                POI = profit / ( (vol_sell+vol_buy)/2/10*buy ) *100
                if profit > 0:
                    profits[tid] = POI
                    print tid
                    print "Profit after tax", profit
                    print "Tax", tax(buy,sell,(vol_sell+vol_buy)/2/10)
                    print "Tax over profit %", tax(buy,sell,(vol_sell+vol_buy)/2/10)/profit*100
                    print "Profit over investment %", profit / ( (vol_sell+vol_buy)/2/10*buy ) *100
                    print
                    continue
        except Exception:
            print "Error", tid
            continue
    result = OrderedDict(sorted(profits.items(), key=itemgetter(1)))
    try:
        with open("resultPOI.txt", "w") as result_file:
            pickle.dump(result, result_file)
    except Exception:
        print "Can't write file"  
        



if __name__ =='__main__':
    main()

##"""
##Example Python EMDR client.
##"""
##import zlib
##import zmq
### You can substitute the stdlib's json module, if that suits your fancy
##import simplejson
##
##def main():
##    context = zmq.Context()
##    subscriber = context.socket(zmq.SUB)
##
##    # Connect to the first publicly available relay.
##    subscriber.connect('tcp://relay-us-central-1.eve-emdr.com:8050')
##    # Disable filtering.
##    subscriber.setsockopt(zmq.SUBSCRIBE, "")
##
##    while True:
##        # Receive raw market JSON strings.
##        market_json = zlib.decompress(subscriber.recv())
##        # Un-serialize the JSON data to a Python dict.
##        market_data = simplejson.loads(market_json)
##        # Dump the market data to stdout. Or, you know, do more fun
##        # things here.
##        print market_data
##        break
##
##if __name__ == '__main__':
##    main()
