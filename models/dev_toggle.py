DEV_INSTANCE_KEY = 'shipspinning.dev'

def queryDev():
    dev = False
    if not db(db.persist_vars.key==DEV_INSTANCE_KEY).count():
        db.persist_vars.insert(key=DEV_INSTANCE_KEY, value=0)
        db.commit()
    else:
        dev = bool(int(db(db.persist_vars.key==DEV_INSTANCE_KEY).select().first().value))

    return dev

def devToggle(harddev=None):
    dev = queryDev()
    if harddev!=None:
        db(db.persist_vars.key==DEV_INSTANCE_KEY).update(value=int(harddev))
    else:
        db(db.persist_vars.key==DEV_INSTANCE_KEY).update(value=int(not dev))
    db.commit()
