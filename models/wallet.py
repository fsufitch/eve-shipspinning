wallet_user_id = '6005794'
wallet_char_id = '90602792'
wallet_api_key = '8CBBA3EC31E54F6FB23E7FE0B77705A5B07CD36B405749E0A781E4A2F4565705'
wallet_corp_id = '98055909'
LAST_REFID_KEY = 'last_refid'
PULL_TIME_KEY = 'pull_time'
WALLET_BALANCE_KEY = 'wallet_balance'

def load_refid():
    refid = 0
    if not db(db.persist_vars.key==LAST_REFID_KEY).count():
        db.persist_vars.insert(key=LAST_REFID_KEY, value=0)
        db.commit()
    else:
        refid = int(db(db.persist_vars.key==LAST_REFID_KEY).select().first().value)

    return refid

def save_refid(refid):
    db(db.persist_vars.key==LAST_REFID_KEY).update(value=refid)
    db.commit()

def load_balance():
    balance = 0
    if not db(db.persist_vars.key==WALLET_BALANCE_KEY).count():
        db.persist_vars.insert(key=WALLET_BALANCE_KEY, value=0)
        db.commit()
    else:
        x = db(db.persist_vars.key==WALLET_BALANCE_KEY).select().first().value
        if x: balance=float(x)
    return balance

def save_balance(balance):
    db(db.persist_vars.key==WALLET_BALANCE_KEY).update(value=str(balance))
    db.commit()

def load_pull_time():
    pull_time = None
    if not db(db.persist_vars.key==PULL_TIME_KEY).count():
        db.persist_vars.insert(key=PULL_TIME_KEY, value=0.0)
        db.commit()
    else:
        from datetime import datetime
        x = db(db.persist_vars.key==PULL_TIME_KEY).select().first().value
        if x:
            pull_time = datetime.fromtimestamp(float(x))
    return pull_time

def save_pull_time(time):
    from time import mktime
    timestamp = mktime(time.timetuple())
    db(db.persist_vars.key==PULL_TIME_KEY).update(value=str(timestamp))
    db.commit()


def pull_wallet_data(override=False):
    if queryDev() and not override:
        return False
    
    last_refid = load_refid()

    eveapi = local_import('eveapi')
    from datetime import datetime
    api = eveapi.EVEAPIConnection()
    auth = api.auth(userID=wallet_user_id, apiKey=wallet_api_key)

    new_refids = []
    latest_row = None
    def process_row(row):
        if str(row.ownerID2) != wallet_corp_id or row.amount < 0 or row.refTypeID!=10:
            return False

        charid = row.ownerID1
        auto_vivify(charid)
        amount = row.amount
        refid = row.refID
        char = db(db.char.charid==charid)
        charrow = char.select().first()
        comment = "Imported via Corp Wallet API"
        if row.reason[6:]:
            comment += "; comment: '%s'" % row.reason[6:].strip()

        if db(db.journal.refid==refid).count() or refid in new_refids: # Already imported
            return False
        new_refids.append(refid)

        charrow.update_record(isk=charrow.isk+amount)
        db.journal.insert(char=charrow, amount=amount, date=datetime.utcnow(), refid=refid, comment=comment)
        db.commit()
        
        return True

    max_rows = 2500 # Arbitrary
    rows = auth.corp.WalletJournal(characterID=wallet_char_id, rowCount=max_rows).entries
    min_refid = 2**64
    max_refid = 0
    for row in rows:
        success = process_row(row)
        if success:
            min_refid = min(min_refid, row.refID)
            max_refid = max(max_refid, row.refID)
            if not latest_row or latest_row.date < row.date:
                latest_row = row

    while len(rows) == max_rows and min_refid > last_refid:
        rows = auth.corp.WalletJournal(characterID=wallet_char_id, rowCount=max_rows, fromID=min_refid).entries
        for row in rows:
            success = process_row(row)
            if success:
                min_refid = min(min_refid, row.refID)
                max_refid = max(max_refid, row.refID)
                if not latest_row or latest_row.date < row.date:
                    latest_row = row

    save_refid(max_refid)

    db.commit()

    if latest_row: # Stuff was actually added
        save_balance(latest_row.balance)
        save_pull_time(get_time())
        return True
    return False

def total_donated_by(char):
    sum_donations = db.journal.amount.sum()
    return db((db.journal.char==char) & (db.journal.refid!=None)).select(sum_donations).first()[sum_donations]

def give_credit(charname, amount, comment):
    c = db(db.char.charname==charname).select().first()
    c.update_record(isk=c.isk+amount)
    db.journal.insert(char=c, amount=amount, date=get_time, comment=comment)
    db.commit()

