import simplejson
import urllib2

import cPickle as pickle
from collections import OrderedDict
from operator import itemgetter
import yaml

def broker_fee (broker_rel, fact_st, corp_st):
    return (1.000 - 0.050 * broker_rel) / 2 ** (0.1400 * fact_st + 0.06000 * corp_st)

BROKER_REL = 5
FACT_ST = 3.44
CORP_ST = 4.62
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
    return typeids

def getTypeIDsFromYAML():
    f = open('typeIDs.yaml','r')
    d = yaml.load(f)
    return d.keys()

def main():
    typeids = getTypeIDsFromText()
    
    profits = {}
    for tid in typeids:
        try:
            request = "http://api.eve-central.com/api/marketstat/json?typeid=%s&usesystem=30000142" % tid
            stream = urllib2.urlopen(request).read()
            d = simplejson.loads(stream.strip("]").strip("["))
            sell = d['sell']['wavg']
            buy = d['buy']['wavg']
            vol_sell = d['sell']['volume']
            vol_buy = d['buy']['volume']
            sell = float(sell)
            buy = float(buy)
            vol_sell = float(vol_sell)
            vol_buy = float(vol_buy)
            vol_avg_10 = (vol_sell + vol_buy)/2/10
            if abs(vol_sell-vol_buy) < 0.2*vol_sell and abs(vol_sell-vol_buy) < 0.2*vol_buy:
                profit = profit_after_tax(buy,sell,vol_avg_10)
                if profit > 0:
                    POI = profit / ( vol_avg_10*buy ) *100
                    tax_10 = tax(buy,sell,vol_avg_10)

                    profits[tid] = {"PAT":profit, "INV":vol_avg_10*buy, "TOP":tax_10/profit*100, "POI": POI}
                    print typeids[tid]
                    print "PAT %s" % '{:20,.2f}'.format(profit)
                    print "INV %s" % '{:20,.2f}'.format(vol_avg_10*buy)
                    print "TOP %s" % '{:20,.2f}'.format(tax_10/profit*100)
                    print "POI %s" % '{:20,.2f}'.format(POI)
                    print
                    continue
        except Exception:
            print "Error", tid
            continue
##    result = OrderedDict(sorted(profits.items(), key=itemgetter(1)))
    try:
        with open(str(datetime.datetime.now()[:-7]), "w") as result_file:
            pickle.dump(profits, result_file)
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
