from urllib2 import urlopen
from lxml import etree
from datetime import timedelta

price_cache_time = timedelta(hours=1)

def fetch_buy_price(typeid, rounding=True, bonusing=True):
    result = 0
    
    bonus_ratio = 0.10
    bonus_max = 30000000

    q = db(db.price_cache.typeid==typeid)
    if q.count()==0 or (get_time() - q.select().first().date > price_cache_time):
        ## Re-fetch data
        region = 10000002 # The Forge
        url = ("http://api.eve-central.com/api/marketstat?typeid=%s&regionlimit=%s" %
               (typeid, region))
        
        response = urlopen(url)
        data = response.read()

        tree = etree.XML(data)
        value = float(tree.xpath('//buy/avg')[0].text)
        if value<1:
            value = float(tree.xpath('//buy/median')[0].text)

        if q.count():
            q.update(price=value, date=get_time())
        else:
            db.price_cache.insert(typeid=typeid, price=value, date=get_time())
        db.commit()

        result = value
    else:
        result = q.select().first().price

    if bonusing:
        result += min(result * bonus_ratio, bonus_max)
    if rounding:
        result = result - (result % 500000) # Be nice and round... down

    return result

def can_payout(award):
    if award.givendate!=None:
        return False
    typeid = award.prize.typeid
    if typeid==None and not award.prize.pack:
        return False
    if award.prize.iskprize!=None and award.prize.iskprize>0.01:
        return False

    return True

def buyout_price(awid, prize=None, rounding=True):
    if not prize:
        award = db.award(awid)
        prize = award.prize
    else:
        if isinstance(prize, int) or isinstance(prize, long):
            print "converting", prize
            prize = db.prize(prize)
            print "--->", prize
    if not prize:
        print "XXX", awid
        return 0

    price = 0
    if prize.pack:
        pack = extract_pack(prize)
        for typeid in pack:
            price += fetch_buy_price(typeid, rounding=False) * pack[typeid][PACKCOUNT]
            #print iskfmt(price), pack[typeid][TYPENAME]
    else:
        price += fetch_buy_price(prize.typeid, rounding=False)

    if rounding:
        # Floor to SIGFIGS figures past normalized decimal
        from math import log, floor
        SIGFIGS = 2
        p10 = floor(log(price,10))
        norm_price = price / (10**p10)
        sig_price = floor(norm_price*(10**SIGFIGS))/(10**SIGFIGS)
        price = sig_price * (10**p10)

    return price


def populate_price_cache(typeids):
    region = 10000002 # The Forge
    url = "http://api.eve-central.com/api/marketstat?regionlimit=%s" % region
    for typeid in typeids:
        url += "&typeid=%s" % typeid

    response = urlopen(url)
    data = response.read()
    tree = etree.XML(data)
    
    for typeid in typeids:
        q = db(db.price_cache.typeid==typeid)

        if q.count()==0 or (get_time() - q.select().first().date > price_cache_time):
            xpath = '//type[@id=\'%s\']/buy' % typeid
            value = float(tree.xpath(xpath+'/median')[0].text)
            if value<1: # for some reason median doesn't exist
                value = float(tree.xpath(xpath+'/mean')[0].text)
        
            if q.count():
                q.update(price=value, date=get_time())
            else:
                db.price_cache.insert(typeid=typeid, price=value, date=get_time())
            db.commit()

def get_sell_prices(typeids):
    timenow = get_time()
    where = db.price_cache_sell.id>0
    for typeid in typeids:
        where = where | (db.price_cache_sell.typeid==typeid)
    cache_rows = db(where).select()
    present_typeids = [r.typeid for r in cache_rows]
    missing_typeids = [t for t in typeids if t not in present_typeids]
    expired_typeids = []
    for row in cache_rows:
        #print row.date, timenow, timenow - row.date, price_cache_time
        if timenow - row.date > price_cache_time:
            expired_typeids.append(row.typeid)
    queried_typeids = missing_typeids + expired_typeids

    region = 10000002 # The Forge

    url = "http://api.eve-central.com/api/marketstat?regionlimit=%s" % region
    for typeid in queried_typeids:
        url += "&typeid=%s" % typeid

    response = {}

    for row in [row for row in cache_rows if row.typeid not in expired_typeids]:
        response[row['typeid']] = row['price']

    #print "present ", present_typeids
    #print "missing ", missing_typeids
    #print "expired ", expired_typeids

    if queried_typeids:
        data = urlopen(url).read()
        tree = etree.XML(data)
        
        for typeid in queried_typeids:
            xpath = '//type[@id=\'%s\']/sell' % typeid
            value = float(tree.xpath(xpath+'/min')[0].text)
            if value<1: # for some reason min doesn't exist
                value = float(tree.xpath(xpath+'/avg')[0].text)
        
            response[typeid] = value

            if typeid in expired_typeids:
                db(db.price_cache_sell.typeid==typeid).update(price=value, date=timenow)
            elif typeid in missing_typeids:
                db.price_cache_sell.insert(typeid=typeid, price=value, date=timenow)
            else:
                raise Exception("The universe is broken and this should have not happened")
        db.commit()
    else:
        #print "no query run"
        pass
    return response
           
def check_reel_stats(reelid, prompt=False, numspins=50000, empirical=False, lockdown=True):
    results = {}

    prizes = db(db.prize.reel==reelid).select()
    reel = db.reel(reelid)
    typeids = []
    for prize in prizes:
        if prize.typeid and not prize.iskprize:
            typeids.append(prize.typeid)
        if prize.pack:
            pack = extract_pack(prize)
            typeids.extend(pack.keys())
    
    prices = get_sell_prices(typeids)

    # Theoretical payout ratio
    numprizes = sum([prize.repeat for prize in prizes])
    payout = 0
    for prize in prizes:
        chance = (float(prize.repeat)/numprizes)**3
        isk = 0
        if prize.iskprize:
            isk = prize.iskprize
        elif prize.pack:
            pack = extract_pack(prize)
            for typeid in pack:
                isk += prices[typeid] * pack[typeid][PACKCOUNT]
        elif prize.typeid:
            isk = prices[prize.typeid]
        else:
            if prompt:
                isk = int(raw_input("ISK price of Prize %s (%s)? " % (prize.id, prize.name)))
            else:
                print "Results tainted!!"
                print "Prize %s (%s) has no TypeID or credit value!"  % (prize.id, prize.name)
                print "Assigning value 0."
        
        payout += isk * chance

    theoretical = payout / reel.spincost
    results['theoretical'] = theoretical
    
    if lockdown:
        if ((theoretical < 0.85) or (theoretical > 0.952)) and not reel.disabled:
            reel.update_record(disabled = True, pricebroken = True)
            db.commit()
        elif ((theoretical > 0.85) and (theoretical < 0.952)) and reel.pricebroken:
            reel.update_record(pricebroken = False)
            db.commit()

    #print "Theoretical payout ratio: %s" % results['theoretical']
    if not empirical:
        return results
    
    # Empirical payout ratio
    type_counts = {}
    sample = chance_statistics(reelid, spinnum=numspins, verbose=False)
    for prizeid in sample:
        prize = db.prize(prizeid)
        if prize.typeid and not prize.iskprize:
            type_counts[prize.typeid] = sample[prizeid]
            

    invested = numspins * reel.spincost
    total = 0
    for typeid in typeids:
        total += prices[typeid] * type_counts.get(typeid, 0)

    results['empirical'] = (total/invested)
    #print "Empirical Ratio:\t%s" % results['empirical']
    return results

