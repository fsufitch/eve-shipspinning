
def auth():
    response.menu = default_menu()
    for menuitem in response.menu:
        if menuitem[0].lower() in ('logout','login'):
            response.menu.remove(menuitem)
            break

    igb = request_is_igb()
    trusted = request_is_trusted() if igb else False
    trust_url = 'http://shipspinning.com' #'http://' + request.env['http_host']

    respdict = {'igb': igb, 'trusted': trusted, 'trust_url': trust_url, 'loginfail': False}

    nexturl = URL('me')
    if 'next' in request.vars:
        nexturl = request.vars['next']
    respdict['nexturl'] = nexturl

    if 'logout' in request.vars:
        logout()
        redirect(URL('default','index'))
    elif check_login(): # Already logged in
        respdict['loggedin'] = True
        respdict['charname'] = get_name_from_id(session.charid)
        redirect(nexturl)
    elif 'submit_form' in request.vars: # trying to log in via form
        charid = get_id_from_name(request.vars['charname'])
        password = request.vars['password']
        login(charid, password)
        if check_login():
            redirect(nexturl)
        else:
            respdict['loginfail'] = True
    elif igb_login(): # Logged in via IGB headers
        respdict['loggedin'] = True
        respdict['charname'] = get_name_from_id(session.charid)
        redirect(nexturl)

    return respdict
    
def add_faux_char():
    if not session.superauth:
        return "Not authorized."
    if 'form_submit' not in request.vars:
        return {'created':False, 'error':None}
    charname = request.vars['charname']
    charid = request.vars['charid']
    password = request.vars['password']
    try:
        isk = float(request.vars['isk'])
    except ValueError:
        return {'created':False, 'error': 'ISK amount needs to be a number.'}

    from sha import sha
    passhash = sha(password).hexdigest()

    try:
        db.char.insert(charid=charid, charname=charname, isk=isk, oogpasshash=passhash)
    except:
        return {'created':False, 'error': "Character already exists"}

    response.flash = "Character created successfully."
    return {'created':True, 'error':None}
 
def me():
    if not check_login():
        login_redirect()
        return
    response.menu = default_menu()
    respdict = {}

    charid = session.charid
    char = get_char_row_from_id(charid)

    if "claim_ajax" in request.vars:
        cash_referrals(char)
        return "success"

    if "claim_bonus_prize_ajax" in request.vars:
        return claim_referral_prize(char, request.vars.get("prize", -1))
    
    charname = char.charname
    respdict['charname'] = charname
    respdict['charid'] = charid
    respdict['char'] = char

    igb_login = (('http_eve_charid' in request.env) and
                 (request.env['http_eve_charid'] == charid))
    respdict['igb_login'] = igb_login

    isk = char.isk
    respdict['isk'] = iskfmt(isk)

    respdict['has_password'] = bool(char.oogpasshash)

    respdict['refcode'] = get_referral_code(charid)

    respdict['unclaimed_refs'] = get_uncashed_referrals(char)
    respdict['claimed_refs'] = get_claimed_referrals(char)
    
    respdict['ref_bonus_prizes'] = get_referral_prizes(char)

    return respdict

def password():
    if not check_login():
        login_redirect()
        return
    response.menu = default_menu()
    respdict = {'error': None, 'success': False}
    charid = session.charid

    charname = get_name_from_id(charid)
    respdict['charname'] = charname

    row = db(db.char.charid==charid).select().first()
    has_password = bool(row.oogpasshash)
    respdict['has_password'] = has_password

    if 'form_submit' in request.vars:
        if has_password and not login(charid, request.vars['oldpass'], dummy=True):
            respdict['error'] = "Incorrect old password."
            return respdict
        if request.vars['newpass'] != request.vars['newpass2']:
            respdict['error'] = "Passwords do not match."
            return respdict

        change_password(charid, request.vars['newpass'])
        respdict['success'] = True
        
    return respdict

def do_wallet_pull():
    success = pull_wallet_data()

    if success:
        return "success"
    
    return "nothing pulled"

def do_prize_total():
    isk = float(calc_prize_total())
    return iskfmt(isk)

def balance():
    if not session.charid:
        return "0 ISK (Not logged in)" #HTTP(401, "Not authorized")
    charid = session.charid
    char = get_char_row_from_id(charid)
    return iskfmt(char.isk)+' ISK'

def spins():
    if not check_login():
        login_redirect()
        return
    response.menu = default_menu()
    respdict = {}
    charid = session.charid

    char = db(db.char.charid==charid).select().first()

    page = request.vars['page'] if 'page' in request.vars else 0
    try:
        page = int(page)-1
        assert page>=0
    except:
        page = 0
    respdict['page'] = page+1

    spp = 20
    numpages = db(db.spin.char==char.id).count()/spp+1
    respdict['numpages'] = numpages
    if page >= numpages:
        page = numpages-1
        respdict['page'] = numpages
    rows = db(db.spin.char==char.id).select(
        db.spin.ALL, db.reel.name, 
        left=db.reel.on(db.reel.id==db.spin.reel),
        orderby=~db.spin.date,
        limitby=(page*spp, (page+1)*spp))
    respdict['rows'] = rows

    return respdict

def wins():
    if not check_login():
        login_redirect()
        return
    response.menu = default_menu()
    respdict = {}
    charid = session.charid

    char = db(db.char.charid==charid).select().first()

    page = request.vars['page'] if 'page' in request.vars else 0
    try:
        page = int(page)-1
        assert page>=0
    except:
        page = 0
    respdict['page'] = page+1

    spp = 20
    numpages = db(db.award.char==char.id).count()/spp+1
    respdict['numpages'] = numpages
    if page >= numpages:
        page = numpages-1
        respdict['page'] = numpages
    rows = db(db.award.char==char.id).select(
        db.award.ALL, 
        orderby=~db.award.date,
        limitby=(page*spp, (page+1)*spp))
    respdict['rows'] = rows

    return respdict

def allwins():
    response.menu = default_menu()
    respdict = {}

    page = request.vars['page'] if 'page' in request.vars else 0
    try:
        page = int(page)-1
        assert page>=0
    except:
        page = 0
    respdict['page'] = page+1

    if 'hideisk' in request.vars:
        if request.vars['hideisk']=='yes':
            session.hideisk = True
        else:
            session.hideisk = False


    query = None
    if session.hideisk:
        query= db((db.award.id>0) & (db.prize.id==db.award.prize) &
                  ((db.prize.iskprize==None) | (db.prize.iskprize<0.01)))
        respdict['hideisk'] = True
    else:
        query = db(db.award.id>0)
        respdict['hideisk'] = False

    spp = 20
    numpages = query.count()/spp+1
    respdict['numpages'] = numpages
    if page >= numpages:
        page = numpages-1
        respdict['page'] = numpages
    rows = query.select(
        db.award.ALL, 
        orderby=~db.award.date,
        limitby=(page*spp, (page+1)*spp))
    respdict['rows'] = rows

    return respdict

def isk_receipts():
    if not check_login():
        login_redirect()
        return
    response.menu = default_menu()
    respdict = {}
    charid = session.charid
    char = db(db.char.charid==charid).select().first()

    page = request.vars['page'] if 'page' in request.vars else 0
    try:
        page = int(page)-1
        assert page>=0
    except:
        page = 0
    respdict['page'] = page+1

    spp = 20
    numpages = db(db.journal.char==char.id).count()/spp+1
    respdict['numpages'] = numpages
    if page >= numpages:
        page = numpages-1
        respdict['page'] = numpages
    rows = db(db.journal.char==char.id).select(
        db.journal.ALL, 
        orderby=~db.journal.date,
        limitby=(page*spp, (page+1)*spp))
    respdict['rows'] = rows

    return respdict
    
def referral():
    response.menu = default_menu()
    respdict = {'refcode': None,
                'found': False,
                'igb': False,
                'trusted': False,
                'charid': None,
                'already_referred': True,
                'selfreferral': True,
                'newplayer': False,
                'referrer_new': True}
    if len(request.args)<1:
        return respdict
    refcode = request.args[0]
    respdict['refcode'] = refcode

    if not db(db.char.refcode==refcode).count():
        return respdict
    respdict['found']=True
    referrer = db(db.char.refcode==refcode).select().first()
    respdict['referrer'] = referrer

    if not request_is_igb():
        return respdict
    respdict['igb'] = True

    if not request_is_trusted():
        return respdict
    respdict['trusted'] = True

    if not igb_login():
        return respdict
    charid = session.charid
    char = get_char_row_from_id(charid)
    
    if referrer.id==char.id:
        return respdict
    respdict['selfreferral'] = False
        
    refquery = db(db.referral.recipient==char)
    if refquery.count():
        respdict['already_referred_referrer'] = refquery.select().first().referrer
        respdict['already_referred'] = True
        return respdict
    respdict['already_referred'] = False


    # If already donated over 1 mil, ineligible
    if total_donated_by(char) > 1000000:
        return respdict
    respdict['newplayer'] = True

    # If referrer is new, that's bad
    if total_donated_by(referrer) < 1000000:
        return respdict
    respdict['referrer_new'] = False

    db.referral.insert(referrer=referrer,
                       recipient=char,
                       date=get_time(),
                       claimed=False)

    amount = 3000000 # New player referral bonus
    comment = "Referral bonus from %s" % referrer.charname
    char.update_record(isk=char.isk+amount)
    db.journal.insert(char=char, amount=amount, date=get_time(), refid=None, comment=comment)

    db.commit()
    return respdict

def index():
    redirect(URL('me'))
