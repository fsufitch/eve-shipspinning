
def get_attribs():
    return db().select(db.attrib.ALL)

def get_attrib_values(att_id):
    q = db(db.attrib_value.attrib==att_id)
    return q.select(db.attrib_value.ALL)

def find_attrib(attname):
    q = db(db.attrib.name==attname)
    rows = q.select(db.attrib.ALL)
    if not len(rows):
        return None
    return rows[0]

def find_attrib_value(val_name, att_id):
    q = db((db.attrib_value.attrib==att_id) & (db.attrib_value.name==val_name))
    rows = q.select(db.attrib_value.ALL)
    if not len(rows):
        return None
    return rows[0]

def get_reel_meta(reel_id, att_id):
    q = db((db.reel_metadata.attrib==att_id) & (db.reel_metadata.reel==reel_id))
    if q.count() == 0:
        return None
    return q.select().first()

def set_reel_meta(reel_id, att_id, val_id):
    q = db((db.reel_metadata.attrib==att_id) & (db.reel_metadata.reel==reel_id))
    if val_id == 0:
        q.delete()
    else:
        if q.count() == 0:
            db.reel_metadata.insert(attrib=att_id, reel=reel_id, value=val_id)
        q.update(value=val_id)
    db.commit()
    
