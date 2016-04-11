ATTRIB_DATA = """
Faction|Amarr Empire|Caldari State|Gallente Federation|Minmatar Republic|Angel Cartel|Serpentis|Guristas|Sansha's Nation|Blood Raider Covenant|Outer Ring Excavations
Meta Group|T1|T2|Empire Faction|Pirate Faction|Deadspace
Profession|Combat|Mining|Industry|Exploration
Miscellaneous|Credit-Only|Monocle Prize|Player-designed
"""

def populate_default_attribs():
    for line in ATTRIB_DATA.split('\n'):
        line = line.strip()
        if not line: continue
        line = line.split('|')
        att_name = line[0]
        att_vals = line[1:]
        if db(db.attrib.name==att_name).count()==0:
            print "Adding attribute: ", att_name
            att_id = db.attrib.insert(name=att_name)
        else:
            print "Attribute already exists: ", att_name
            att_id = db(db.attrib.name==att_name).select().first()
        for val in att_vals:
            if db((db.attrib_value.name==val) & (db.attrib_value.attrib==att_id)).count()==0:
                print " -- Adding attribute value: ", val
                db.attrib_value.insert(attrib=att_id, name=val)
            else:
                print " -- Attribute value already exists: ", val
    db.commit()
    print 'Done.'

def nuke_attribs():
    db.attrib.truncate()
    db.attrib_value.truncate()
    db.reel_metadata.truncate()
    db.commit()
