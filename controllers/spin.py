
def download():
    return response.download(request, db)


def go():
    noauth = False
    if not check_login():
        noauth=True
    if len(request.args)==0:
        redirect(URL('stations','all'))
        return
    response.menu = default_menu()
    respdict = {}
    respdict['noauth'] = noauth

    reelid = request.args[0]
    reel = db(db.reel.id == reelid).select().first()
    respdict['reel'] = reel

    if 'spin_ajax' in request.vars:
        if noauth:
            return "noauth"
        if reel.disabled:
            return "disabled"
        char = db(db.char.charid==session.charid).select().first()
        isk = char.isk
        if isk < reel.spincost:
            return "$$$"
        newisk = isk - reel.spincost
        results = spin_reel(reelid)
        aw_id = None

        if results.count(results[0])==len(results):
            # Win!
            prize = db.prize(results[0])
            if prize.iskprize>0.01: # It's an ISK prize
                newisk += prize.iskprize
                aw_id = db.award.insert(char=char.id, prize=results[0], date=get_time(), givendate=get_time())
                db.journal.insert(char=char.id, amount=prize.iskprize, date=get_time(),
                                  comment="Won via spinning (%s)" % aw_id)
            else: # It's an item prize
                aw_id = db.award.insert(char=char.id, prize=results[0], date=get_time(), givendate=None)

        char.update_record(isk=newisk)
        db.spin.insert(char=char.id, reel=reelid, date=get_time(), award=aw_id)
        db.commit()
        
        import json
        return json.dumps(results)

    prizes = db(db.prize.reel == reelid).select(db.prize.ALL)
    respdict['prizes'] = prizes
    
    return respdict

def index():
    redirect(URL('stations','browse'))
