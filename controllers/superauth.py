def index():
    if 'logout' in request.vars:
        session.superauth = False
    elif 'toggledev' in request.vars:
        devToggle()
    elif 'submit_form' in request.vars:
        pwd = request.vars['password']
        from sha import sha
        h = 'XXXXX'
        if sha(pwd).hexdigest()==h:
            session.superauth = True

    return {'auth':session.superauth}
