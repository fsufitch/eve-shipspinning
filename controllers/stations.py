
def download():
    return response.download(request, db)

def all():
    response.menu = default_menu()
    respdict = {}

    reellist = []
    rows = db().select(db.reel.ALL, orderby=db.reel.weight)
    rowlist = [row for row in rows]
    respdict['reels'] = rowlist

    return respdict

def browse():
    response.menu = default_menu()
    respdict = {}

    attribs = get_attribs()
    respdict['attribs'] = attribs

    attrib_values = {}
    for attrib in attribs:
        vals = get_attrib_values(attrib.id)
        vallist = [(v.id, v.name) for v in vals]
        attrib_values[attrib.id] = vallist
    respdict['attrib_values'] = attrib_values
    from json import dumps as json_dump
    respdict['attrib_values_json'] = json_dump(attrib_values).replace("'","\\'")

    reels = []
    respdict['query_att'] = ''
    respdict['query_val'] = ''
    if len(request.args)==2:
        att_id = request.args[0]
        val_id = request.args[1]
        respdict['query_att'] = att_id
        respdict['query_val'] = val_id
        q = db((db.reel_metadata.attrib==att_id) & (db.reel_metadata.value==val_id))
        res = q.select(db.reel_metadata.reel, orderby=db.reel_metadata.reel.name)
        reels = [x.reel for x in res]
    elif len(request.args)==1 and request.args[0]=='all':
        res = db().select(db.reel.ALL, orderby=db.reel.name)
        reels = [x for x in res]
    else:
        redirect(URL('stations', 'browse', args=['all']))
        return
    reels = filter((lambda r: not r.hidden), reels)
    respdict['reels'] = reels

    #from random import shuffle
    prizes = {}
    for reel in reels:
        prizelist = []
        res = db(db.prize.reel==reel).select(db.prize.ALL, orderby=db.prize.repeat)
        for prize in res:
            prizelist.append( (
                    prize.id,
                    prize.typeid,
                    prize_imgurl(prize.id, size=64),
                    prize.name,
                    prize.iskprize<0.01 and not prize.pack) )
        #shuffle(imglist)
        prizes[reel.id] = prizelist
    respdict['prizes'] = prizes
        
    return respdict

def view_reel():
    response.menu = default_menu()
    respdict = {}
    reelid = request.args[0]
    reel = db.reel(reelid)

    respdict['reel'] = reel

    prizes = db(db.prize.reel == reelid).select(db.prize.ALL)
    from random import shuffle
    prizes = list(prizes)
    shuffle(prizes)
    respdict['prizes'] = prizes

    payout = check_reel_stats(reel.id, empirical=False)['theoretical']
    respdict['payout'] = "%.2f" % (payout*100)
    respdict['payout'] = "%.2f" % (payout*100)
    respdict['payoutnum'] = payout

    return respdict
    

def new_reel():
    if not session.superauth:
        return "Not authorized."
    response.menu = default_menu()
    respdict = {}
    form = SQLFORM(db.reel)
    if form.accepts(request.vars, session):
        response.flash = "Reel added successfully."
        redirect(URL('stations','browse', args=['all']))
    elif form.errors:
        response.flash = "Error in form!"
    respdict['form'] = form
    return respdict


def edit_reel():
    if not session.superauth:
        return "Not authorized"
    response.menu = default_menu()
    respdict = {'reellist': False}
    if not len(request.args):
        reels = db().select(db.reel.ALL, orderby=db.reel.weight)
        return {'reellist': True, 'reels': reels}
    reelid = request.args[0]
    reel = db(db.reel.id == reelid).select().first()
    respdict['reel'] = reel

    form = SQLFORM(db.reel, reel)
    if form.accepts(request.vars, session):
        response.flash = "Reel added successfully."
        redirect(URL('stations','browse', args=['all']))
    elif form.errors:
        response.flash = "Error in form!"
    respdict['form'] = form

    db.prize.reel.default = reel.id
    prizeform = SQLFORM(db.prize)
    if prizeform.accepts(request.vars, session):
        response.flash = "Prize added successfully."
    elif form.errors:
        response.flash = "Error in form!"
    respdict['prizeform'] = prizeform

    if 'remove' in request.vars:
        removeid = request.vars['remove']
        db(db.prize.id == removeid).delete()
        response.flash = "Prize removed."

    prizes = db(db.prize.reel == reelid).select(db.prize.ALL)
    respdict['prizes'] = prizes

    return respdict

def balance_reel():
    if not session.superauth:
        return "Not authorized"

    response.menu = default_menu()
    respdict = {'reellist': False}
    if not len(request.args):
        reels = db().select(db.reel.ALL, orderby=db.reel.weight)
        return {'reellist': True, 'reels': reels}

    reelid = request.args[0]
    reel = db(db.reel.id == reelid).select().first()
    respdict['reel'] = reel

    if request.vars.get('enable'):
        reel.update_record(disabled = False)
    if request.vars.get('disable'):
        reel.update_record(disabled = True)
    if request.vars.get('unbreak'):
        reel.update_record(pricebroken = False)
        

    if request.vars.get('rpc'):
        # return results as JSON
        if request.vars.get('empirical'):
            return check_reel_stats(reelid, numspins=1000, empirical=True)['empirical']
    if request.vars.get('submit'):
        prizes = db(db.prize.reel == reelid).select(db.prize.ALL)
        changed = False
        for p in prizes:
            repeat = request.vars.get("prize_"+str(p.id))
            print repeat,p.repeat
            if repeat != p.repeat:
                p.update_record(repeat=repeat)
                changed = True
        if changed:
            db.commit()

    respdict['theoretical'] = check_reel_stats(reelid, lockdown=True)['theoretical']

    prizes = db(db.prize.reel == reelid).select(db.prize.ALL)
    respdict['prizes'] = prizes

    # Refresh after changes
    reel = db(db.reel.id == reelid).select().first() 
    respdict['reel'] = reel

    return respdict

def meta_reel():
    if not session.superauth:
        return "Not authorized"
 
    if request.vars.get('submit'):
        reelid = request.args[0]
        for attrib in get_attribs():
            val_id = request.vars.get('s_'+str(attrib.id))
            set_reel_meta(reelid, attrib.id, val_id)
            
    response.menu = default_menu()

    respdict = {'reellist': False}
    if not len(request.args):
        reels = db().select(db.reel.ALL, orderby=db.reel.weight)
        return {'reellist': True, 'reels': reels}

    reelid = request.args[0]
    reel = db(db.reel.id == reelid).select().first()
    respdict['reel'] = reel
    
    attribs = get_attribs()
    respdict['attribs'] = attribs

    attrib_values = {}
    for attrib in attribs:
        vals = get_attrib_values(attrib.id)
        vallist = [(v.id, v.name) for v in vals]
        attrib_values[attrib.id] = vallist
    respdict['attrib_values'] = attrib_values

    attrib_selected = {}
    for attrib in attribs:
        val = get_reel_meta(reelid, attrib.id)
        attrib_selected[attrib.id] = (val.value.id if val else 0)
    respdict['attrib_selected'] = attrib_selected

    return respdict

def reel_check_cron():
    reels = db().select(db.reel.ALL)
    response = ""
    for reel in reels:
        response += reel.name + str(check_reel_stats(reel.id, empirical=False, lockdown=True)['theoretical']) + "\n"
    return response
