from datetime import datetime

def logout():
    session.charid = None
    
def igb_login():
    if 'http_eve_charid' not in request.env:
        return False
    charid = request.env['http_eve_charid']
    auto_vivify(charid)
    session.charid = charid
    return True

def login(charid, password, dummy=False):
    from sha import sha
    passhash = sha(password).hexdigest()
    q = db(db.char.charid==charid)
    if not q.count():
        return False
    if passhash == q.select().first().oogpasshash:
        if not dummy: session.charid = charid
        return True
    return False

def check_login():
    good = True
    if not session.charid and not igb_login():
        good = False
    if not good:
        logout()
    return good
        
def change_password(charid, password):
    from sha import sha
    passhash = sha(password).hexdigest()
    
    db(db.char.charid == charid).update(oogpasshash=passhash)
    db.commit()

def user_is_agent():
    return check_login() and get_char_row_from_id(session.charid).agent
