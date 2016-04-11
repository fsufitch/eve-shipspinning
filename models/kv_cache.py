def mk_timestamp_key(KEY):
    return str(KEY)+"++kv_cache_timestamp"

def kv_cache_sane(KEY, default=""):
    from datetime import datetime
    STAMP_KEY = mk_timestamp_key(KEY)
    if not db(db.persist_vars.key==STAMP_KEY).count():
        calc_time = datetime.utcfromtimestamp(0) # Epoch, never calculated before
        from time import mktime
        timestamp = mktime(calc_time.timetuple())
        db.persist_vars.insert(key=STAMP_KEY, value=timestamp)
        db.commit()
    if not db(db.persist_vars.key==KEY).count():
        db.persist_vars.insert(key=KEY, value=default)
        db.commit()

def kv_cache_get_timedelta(KEY):
    from datetime import datetime
    STAMP_KEY = mk_timestamp_key(KEY)
    now = datetime.utcnow()
    
    calc_time = None
    if not db(db.persist_vars.key==STAMP_KEY).count():
        calc_time = datetime.utcfromtimestamp(0) # Epoch, never calculated before
        from time import mktime
        timestamp = mktime(calc_time.timetuple())
        db.persist_vars.insert(key=STAMP_KEY, value=timestamp)
        db.commit()
    else:
        x = db(db.persist_vars.key==STAMP_KEY).select().first().value
        if x:
            calc_time = datetime.utcfromtimestamp(float(x))
    return calc_time-now

def kv_cache_get_value(KEY):
    return db(db.persist_vars.key==KEY).select().first().value

def kv_cache_set_value(KEY, value):
    from time import mktime
    timestamp = mktime(get_time().timetuple())
    STAMP_KEY = mk_timestamp_key(KEY)
    db(db.persist_vars.key==KEY).update(value=value)
    db(db.persist_vars.key==STAMP_KEY).update(value=str(timestamp))
    db.commit()

