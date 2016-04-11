eveapi = local_import('eveapi')

def is_igb():
    return 'http_eve_charid' in request.env

def auto_vivify(charid):
    if db(db.char.charid==charid).count():
        return  # character id already exists in db
    
    api = eveapi.EVEAPIConnection()
    try:
        el = api.eve.CharacterName(ids=str(charid))
        charname = el.characters[0].name
    
        db.char.insert(charid=charid, charname=charname, isk=0, oogpasshash=None)
        return True
    except eveapi.Error:
        return False

def get_char_row_from_id(charid):
    q = db(db.char.charid==charid)
    if not q.count():
        if auto_vivify(charid):
            q = db(db.char.charid==charid)
        else:
            raise ValueError('Invalid character id:', charid)
    
    char = q.select().first()
    return char

def get_name_from_id(charid):
    return get_char_row_from_id(charid).charname

def get_id_from_name(charname):
    q = db(db.char.charname==charname)
    if not q.count():
        return None
    charid = q.select()[0].charid
    return charid

TYPENAME = 'evedb.typename'
PACKCOUNT = 'prizepack.count'
PACKIMG = 'prizepack.image_url'
PACKDATA_CACHE = {} # md5 : extracted pack
def extract_pack(prizeid):
    q = db(db.prize.id==prizeid)
    prize = q.select().first()
    packdata = prize.pack

    if not packdata: return None

    from hashlib import md5
    packhash = md5(packdata).hexdigest()
    if packhash in PACKDATA_CACHE:
        return PACKDATA_CACHE[packhash]
    
    from json import loads
    try:
        data = loads(packdata)
    except:
        return "invalid pack data: "+packdata
    output = {}
    for typeid in data:
        fragment = {}
        fragment[TYPENAME] = data[typeid]['NAME']
        fragment[PACKCOUNT] = data[typeid]['COUNT']
        url = data[typeid]['DISPLAY']
        if url=='Type':
            url = 'http://image.eveonline.com/Type/%s_64.png' % typeid
        elif url=='Render':
            url = 'http://image.eveonline.com/Type/%s_64.png' % typeid
        fragment[PACKIMG] = url
        output[typeid] = fragment

    PACKDATA_CACHE[packhash] = output
    return output

def prize_details(prizeid):
    q = db(db.prize.id==prizeid)
    prize = q.select().first()

    pack = extract_pack(prizeid)
    
    if pack: 
        details = {'NAME': prize.name}
        details.update(pack)
        return (True, details)

    if prize.iskprize > 0.01:
        return (False, "Credit: "+ iskfmt(prize.iskprize) +" ISK")
    return (False, prize.name)

def iskfmt(isk):
    commafy = lambda x: commafy(x/1000)+','+'0'*(3-len(str(x%1000)))+str(x%1000) if x>999 else str(x)
    decimals = ("%.2f" % isk).split('.')[1]
    return commafy(int(isk))+'.'+decimals

def prize_imgurl(prizeid, size=128):
    prize = db.prize(prizeid)
    url = prize.imgurl
    if url=='Type' or url=='Render':
        typeid = prize.typeid
        if url=='Type' and size > 64:
            size = 64
        url = "http://image.eveonline.com/%s/%s_%s.png" % (url, typeid, size)
    return url

def prize_imgmeta(prizeid, size=128):
    packoverlay = URL("static","images/pack64.png")
    if size > 64:
        packoverlay = URL("static","images/pack128.png")
    imgurl = prize_imgurl(prizeid, size)
    pack = bool(extract_pack(prizeid))
    return (imgurl, pack, packoverlay)
        
def prize_price(prize):
    typeid = prize.typeid
    price = 0
    if typeid and (not prize.iskprize or prize.iskprize<0.01):
        price = fetch_buy_price(typeid, rounding=False, bonusing=False)
    else:
        price = prize.iskprize
    return price


def spin_reel(reel_id):
    prizes = db(db.prize.reel == reel_id).select()
    reel = []
    
    for prize in prizes:
        reel += prize.repeat * [prize.id]

    from random import choice as random_choice
    from random import shuffle

    shuffle(reel)

    c1 = random_choice(reel)
    c2 = random_choice(reel)
    c3 = random_choice(reel)

    return c1, c2, c3

def chance_statistics(reel_id, spinnum=10000, respin=True, cashin=False, verbose=True):
    reel = db.reel(reel_id)
    cost = reel.spincost
    isk = cost*spinnum
    startisk = isk
    print "Starting with %s ISK" % iskfmt(startisk)
    iskwon = 0
    prizes = db(db.prize.reel==reel_id).select()
    iskprizes = {}
    for prize in prizes:
        if prize.iskprize>0.01:
            iskprizes[prize.id] = prize.iskprize
            if verbose:
                print "isk prize", prize

    results = {}
    actualspins = 0
    loss_streaks = []
    losses = 0
    def spin():
        c1, c2, c3 = spin_reel(reel_id)
        
        if c1==c2 and c2==c3:
            if c1 not in results:
                results[c1] = 0
            results[c1] += 1
            if c1 in iskprizes:
                return True, iskprizes[c1], None
            return True, 0, c1
            
        return False, 0, None
        
    standby_prizes = []
    investisk = isk

    while isk>=cost:
        if verbose and int(isk)%int(cost*spinnum/10)==0:
            print "%.2f" % (isk/cost)
        isk -= cost
        (win, iskwin, prize) = spin()
        if win:
            loss_streaks.append(losses)
            losses = 0
            if not iskwin:
                standby_prizes.append(prize)
        else:
            losses += 1
        if respin:
            isk += iskwin
                
        iskwon += iskwin
        actualspins +=1

        if isk<cost and cashin: # If we're about to lose, try to cash in items
            cashed_prize_isk = 0
            sell_prize_isk = 0
            for p in standby_prizes:
                if not p:
                    print "Null prize?", p
                    continue
                p = db.prize(p)
                cash_value = buyout_price(None, p)
                cashed_prize_isk += cash_value
                typeids = [p.typeid] if not p.pack else extract_pack(p)
                for t in typeids:
                    sell_prize_isk += get_sell_prices(typeids)[t]
                    
            print "Cashed in: %s ISK (%.2f%%)" % (iskfmt(cashed_prize_isk), 100*cashed_prize_isk/investisk)
            investisk = cashed_prize_isk

            if cashed_prize_isk+isk>startisk:
                print "ALERT: %s ISK after cash-in > %s ISK start ISK" % (iskfmt(isk+cashed_prize_isk), iskfmt(startisk))
            if sell_prize_isk>startisk:
                print "XXX PLAYER WINNING: %s ISK > %s ISK" % (iskfmt(sell_prize_isk), iskfmt(startisk))

            isk += cashed_prize_isk
            cashed_prize_isk = 0
            standby_prizes = []
            

    for key in results:
        name = db(db.prize.id==key).select().first().name
        if verbose:
            print key, results[key], name

    if verbose:
        print "Spins:", actualspins
        print "Average loss streak", float(sum(loss_streaks))/len(loss_streaks)
        print "Shortest loss streak:", min(loss_streaks)
        print "Longest loss streak:", max(loss_streaks)
        print "Start ISK:", iskfmt(startisk)
        print "ISK paid out:", iskfmt(iskwon)

    return results

def get_time():
    from datetime import datetime
    return datetime.utcnow()

def login_redirect():
    redirect(URL('char', 'auth', vars={'next': URL()}))
