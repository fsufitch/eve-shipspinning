def wins():
    response.headers['Content-Type'] = 'application/atom+xml'

    query = None

    ships_only = 'ships' in request.vars
    ungiven = 'ungiven' in request.vars
    condition = db.award.id > 0
    if ships_only: 
        condition = (condition & (db.prize.id==db.award.prize) &
                   ((db.prize.iskprize==None) | (db.prize.iskprize<0.01)))
    if ungiven:
        condition = condition & (db.award.givendate==None)
    
    query = db(condition)
    
    spp = 20
    rows = query.select(
        db.award.ALL, 
        orderby=~db.award.date,
        limitby=(0,30))

    respdict = {}
    respdict['ships_only'] = ships_only
    respdict['time'] = get_time()
    winlist = []
    respdict['winlist'] = winlist

    for row in rows:
        rr = {}
        rr['charname'] = row.char.charname
        rr['prizename'] = row.prize.name
        rr['time'] = row.date
        winlist.append(rr)

    return respdict
