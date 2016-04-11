def give_prizes():
    if not check_login():
        login_redirect()
        return
    if not user_is_agent():
        return "You are not a Ship Spinning Inc. agent. Go away."
    charid = session.charid
    char = get_char_row_from_id(charid)
    respdict = {}
    respdict['char'] = char
    response.menu = default_menu()

    rows = db(db.award.givendate==None).select(db.award.ALL,
                                          orderby=db.award.date,
                                          )
    respdict['rows'] = rows

    return respdict

def give():
    if not check_login():
        return HTTP(401, "Not authorized")
    charid = session.charid
    char = db(db.char.charid==charid).select().first()
    if not char.agent:
        return HTTP(401, "Not authorized")
    awardid = request.vars['id']

    results = {}
    results['awardid'] = awardid
    results['updated'] = False
    
    award = db.award(awardid)
    if award.givendate==None:
        award.update_record(givendate=get_time(), agent=char)
        results['updated'] = True

    import json
    return json.dumps(results)
    
def charlist():
    if not check_login():
        login_redirect()
        return
    if not user_is_agent():
        return "You are not a Ship Spinning Inc. agent. Go away."

    response.menu = default_menu()

    chars = []
    for row in db().select(db.char.ALL, orderby=db.char.charname):
        chars.append(row)

    return {'chars':chars}

def view_wallet():
    if not check_login():
        login_redirect()
        return
    if not user_is_agent():
        return "You are not a Ship Spinning Inc. agent. Go away."
    response.menu = default_menu()
    respdict = {}

    page = request.vars['page'] if 'page' in request.vars else 0
    try:
        page = int(page)-1
        assert page>=0
    except:
        page = 0
    respdict['page'] = page+1

    spp = 20
    numpages = db(db.journal.refid!=None).count()/spp+1
    respdict['numpages'] = numpages
    if page >= numpages:
        page = numpages-1
        respdict['page'] = numpages
    rows = db(db.journal.refid!=None).select(
        orderby=~db.journal.date,
        limitby=(page*spp, (page+1)*spp))
    respdict['rows'] = rows

    respdict['pull_time'] = load_pull_time()
    respdict['balance'] = load_balance()

    return respdict

    

def index():
    redirect(URL('agent','give_prizes'))
