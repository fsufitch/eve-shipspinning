def faq():
    response.menu = default_menu()
    return {}

def promise():
    response.menu = default_menu()
    return {}

def home():
    response.menu = default_menu()
    respdict = {}

    newspost = db().select(db.news.ALL, orderby=~db.news.date).first()
    respdict['newspost'] = newspost

    rows = db().select(db.spin.ALL, orderby=~db.spin.date, limitby=(0,50))
    reels = {}
    for row in rows:
        if row.reel not in reels:
            reels[row.reel] = 0
        reels[row.reel] += 1
    sorted_reels = reels.keys()
    sorted_reels.sort(key=lambda k: 0-reels[k])
    respdict['popular'] = sorted_reels[0]

    prizes = db(db.prize.reel == sorted_reels[0]).select(db.prize.ALL)
    from random import shuffle
    prizes = list(prizes)
    shuffle(prizes)
    respdict['prizes'] = prizes

    query= db((db.award.id>0) & (db.prize.id==db.award.prize) &
              ((db.prize.iskprize==None) | (db.prize.iskprize<0.01)))
    winners = query.select(db.award.ALL, 
                           orderby=~db.award.date,
                           limitby=(0,10))
    respdict['winners'] = winners

    respdict['prizeisk'] = get_prize_total()
    respdict['numplayers'] = db(db.char.id>0).count()
    respdict['numships'] = db((db.prize.iskprize==None) | (db.prize.iskprize<0.01)).count()

    return respdict

def news():
    response.menu = default_menu()
    respdict = {}

    char = None
    if check_login():
        char = get_char_row_from_id(session.charid)
    respdict['char'] = char
    
    postid = 0
    if len(request.args)==0:
        respdict['homeview'] = True
    else:
        respdict['homeview'] = False
        postid = request.args[0]

    post = None
    if postid:
        post = db(db.news.id == postid).select().first()
    else:
        post = db().select(db.news.ALL, orderby=~db.news.date).first()
    respdict['post'] = post

    comments = db(db.comment.post == post).select(orderby=db.comment.date)
    respdict['comments'] = comments

    return respdict

def new_post():
    response.menu = default_menu()
    if not check_login():
        login_redirect()
        return
    charid = session.charid
    char = db(db.char.charid==charid).select().first()
    if not char.agent:
        return "You are not a Ship Spinning Inc. agent. Go away."
    respdict = {}
    respdict['char'] = char

    if 'form_submit' in request.vars:
        title = request.vars['title']
        body = request.vars['body']
        db.news.insert(title=title, body=body, date=get_time(), author=char)
        response.flash = "News post added."

    return respdict

def edit_post():
    response.menu = default_menu()
    if not check_login():
        login_redirect()
        return
    charid = session.charid
    char = db(db.char.charid==charid).select().first()
    if not char.agent:
        return "You are not a Ship Spinning Inc. agent. Go away."
    respdict = {}
    respdict['char'] = char

    postid = 0
    if len(request.args)==0:
        redirect(URL('general','news'))
        return ''
    else:
        postid = request.args[0]
    post = db.news(postid)
    respdict['post'] = post
        
    if 'form_submit' in request.vars:
        title = request.vars['title']
        body = request.vars['body']
        post.update_record(title=title, body=body, editdate=get_time(), editauthor=char)
        response.flash = "Post successfully edited."

    return respdict

def archive():
    response.menu = default_menu()
    respdict = {}
    
    posts = db().select(db.news.ALL, orderby=~db.news.date)
    respdict['posts'] = posts

    return respdict

def stats():
    """ Statistics for the whole site """
    response.menu = default_menu()
    respdict = {}

    respdict['total_prize_isk'] = get_prize_total()
    respdict['num_players'] = get_num_players()
    respdict['num_real_prizes'] = get_num_real_prizes()
    respdict['total_credit_codes'] = get_total_credit_codes()

    return respdict
