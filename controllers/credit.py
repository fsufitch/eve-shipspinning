def manage_codes():
    if not check_login():
        login_redirect()
        return
    if not user_is_agent():
        return "You are not a Ship Spinning Inc. agent. Go away."
    charid = session.charid
    char = get_char_row_from_id(charid)

    respdict = {}
    response.menu = default_menu()

    form = SQLFORM(db.credit_code)
    if form.accepts(request.vars, session):
        response.flash = "Code added successfully."
    elif form.errors:
        response.flash = "Error in form!"
    respdict['form'] = form

    rows = db().select(db.credit_code.ALL)
    respdict['rows'] = rows

    return respdict

def toggle_active():
    if not user_is_agent():
        return "You are not a Ship Spinning Inc. agent. Go away."

    id = request.vars['id']
    row = db.credit_code(id)
    newstatus = not row.active
    row.update_record(active=newstatus)
    db.commit()

    response = {'id': id, 'status': newstatus}

    import json
    return json.dumps(response)

def my_codes():
    if not check_login():
        login_redirect()
        return
    respdict = {}
    response.menu = default_menu()

    charid = session.charid
    char = get_char_row_from_id(charid)

    if 'submit_form' in request.vars:
        codetxt = request.vars['code']
        print codetxt
        q = db(db.credit_code.code==codetxt)
        if not q.count():
            response.flash = '"'+codetxt+'" is not a valid credit code.'
        else:
            code = q.select().first()
            if not code.active:
                response.flash = "The code \"%s\" is inactive. Check your sources." % code.code
            elif db((db.claim.char==char)&(db.claim.credit_code==code)).count():
                response.flash = "You have already used \"%s\". Look in the table." % code.code
            else:
                newisk = char.isk + code.isk
                char.update_record(isk=newisk)
                db.claim.insert(char=char, credit_code=code, date=get_time())
                db.journal.insert(char=char, amount=code.isk, comment="CC "+code.code, date=get_time())
                db.commit()
                response.flash = "\"%s\" activated! %s ISK granted." % (code.code, iskfmt(code.isk))

    codes = db(db.claim.char==char).select(orderby=db.claim.date)
    respdict['codes'] = codes

    return respdict

def claims():
    if not check_login():
        login_redirect()
        return
    if not user_is_agent():
        return "You are not a Ship Spinning Inc. agent. Go away."
    response.menu = default_menu()
    respdict = {}
    charid = session.charid

    char = get_char_row_from_id(charid)

    page = request.vars['page'] if 'page' in request.vars else 0
    try:
        page = int(page)-1
        assert page>=0
    except:
        page = 0
    respdict['page'] = page+1

    q = db(db.claim.id>0)
    spp = 20
    numpages = q.count()/spp+1
    respdict['numpages'] = numpages
    if page >= numpages:
        page = numpages-1
        respdict['page'] = numpages
    rows = q.select(
        db.claim.ALL, 
        orderby=~db.claim.date,
        limitby=(page*spp, (page+1)*spp))
    respdict['rows'] = rows

    return respdict
