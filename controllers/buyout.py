def index():
    if not check_login():
        login_redirect()
        return
    response.menu = default_menu()
    respdict = {}
    charid = session.charid

    char = get_char_row_from_id(charid)

    nongiven_awards = db((db.award.char==char)&(db.award.givendate==None)).select(orderby=db.award.date)

    payout_awards = []
    for award in nongiven_awards:
        if can_payout(award):
            payout_awards.append(award)

    respdict['awards'] = payout_awards

    return respdict

def get_price():
    awid = request.vars['awid']
    award = db.award(awid)
    if not award: raise HTTP(404, "No such award")

    price = buyout_price(awid)
    
    response = {'awid': awid, 'price': iskfmt(price)+" ISK"}
    import json
    return json.dumps(response)

def buyout_credit():
    if not check_login():
        raise HTTP(403, "Not logged in")
    charid = session.charid
    char = get_char_row_from_id(charid)

    awid = request.vars['awid']
    award = db.award(awid)
    if not award: raise HTTP(404, "No such award")

    if award.char.id!=char.id: raise HTTP(403, "This award does not belong to the logged in character")

    if award.givendate!=None:
        return {'awid': awid, 'already_processed':True}

    price = buyout_price(awid)
    award.update_record(givendate=get_time())
    char.update_record(isk=char.isk+price)
    db.journal.insert(char=char, amount=price, date=get_time,
                      comment="Buyout for %s (ID: %s)" % (award.prize.name,award.id))
    db.buyout.insert(award=award, isk=price)
    db.commit()

    import json
    return json.dumps({'awid': awid, 'already_processed':False})
    
