def get_num_players():
    return db(db.char.id>0).count()

def get_num_real_prizes():
    return db((db.prize.iskprize==None) | (db.prize.iskprize<0.01)).count()

def get_total_credit_codes():
    total = 0
    for row in db(db.claim.id>0).select():
        total += row.credit_code.isk
    return total

### REEL TOTALS

REEL_TOTALS_KEY = 'reel_totals'

def calc_reel_totals(force=False, hideisk=False):
    kv_cache_sane(REEL_TOTALS_KEY, default=str({}))

    delta = kv_cache_get_timedelta(REEL_TOTALS_KEY)
    if (not force) and (delta < timedelta(minutes=59)):
        as_str = kv_cache_get_value(REEL_TOTALS_KEY)
        from json import loads
        return loads(as_str)

    reel_totals = {}
    
    reels = db(db.reel.id>0).select()
    for r in reels:
        query = (db.prize.reel==r.id)
        if hideisk:
            query = ( query &
                      ( (db.prize.iskprize==None) | 
                        (db.prize.iskprize<0.01)
                        ) 
                      ) 
        query = ( query &
                  (db.award.prize==db.prize.id)
                  )
            

        query = db(query)
        rows = query.select(db.award.ALL)
        total = 0
        for row in rows:
            price = prize_price(row.prize)
            total += price
        reel_totals[r.id] = total

    if not hideisk:
        from json import dumps
        value = dumps(reel_totals)
        kv_cache_set_value(REEL_TOTALS_KEY, value)

    return reel_totals
    
    
def get_reel_totals():
    kv_cache_sane(REEL_TOTALS_KEY, default=str({}))
    as_str = kv_cache_get_value(PRIZE_TOTAL_KEY)
    from json import loads
    return loads(as_str)


### PRIZE TOTAL

PRIZE_TOTAL_KEY = 'prize_total_won'

def calc_prize_total(force=False, hideisk=False):
    from datetime import datetime, timedelta
    kv_cache_sane(PRIZE_TOTAL_KEY, default=str(0.0))

    delta = kv_cache_get_timedelta(PRIZE_TOTAL_KEY)
    if (not force) and (delta < timedelta(minutes=59)):
        isk = kv_cache_get_value(PRIZE_TOTAL_KEY)
        return float(isk)

    prizes = db().select(db.award.ALL)
    query = None
    if hideisk:
        query= db((db.award.id>0) & (db.prize.id==db.award.prize) &
                  ((db.prize.iskprize==None) | (db.prize.iskprize<0.01)))
    else:
        query = db(db.award.id>0)
    rows = query.select(db.award.ALL)#, orderby=~db.award.date, limitby=(0,20))

    isktotal = 0
    typeids = []
    for row in rows:
        typeid = row.prize.typeid
        if typeid and (not row.prize.iskprize or row.prize.iskprize<0.01):
            typeids.append(typeid)
    typeids = list(set(typeids))
    populate_price_cache(typeids)
    for row in rows:
        price = prize_price(row.prize)
        isktotal += price

    if not hideisk:
        from time import mktime
        value = format(isktotal, ".2f")
        kv_cache_set_value(PRIZE_TOTAL_KEY, value)

    return isktotal

def get_prize_total():
    kv_cache_sane(PRIZE_TOTAL_KEY, default=str(0.0))
    isk = kv_cache_get_value(PRIZE_TOTAL_KEY)
    return float(isk)
