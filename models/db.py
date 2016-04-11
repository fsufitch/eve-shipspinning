db = DAL('sqlite://storage.db')

db.define_table('char',
                Field('charid', required=True, unique=True),
                Field('charname', required=True),
                Field('isk', 'double', default=0),
                Field('oogpasshash'),
                Field('agent', 'boolean', default=False),
                Field('refcode', default=None),
                Field('bonus_mult', 'double', required=True, default=0),
                Field('ref_bonuses_used', 'list:integer', default=[])
                )

db.define_table('reel',
                Field('name', required=True),
                Field('description', 'text', required=True),
                Field('spincost', 'double', required=True),
                Field('img', 'upload', autodelete=True, requires=IS_IMAGE()),
                Field('weight', 'integer', default=0),
                Field('hidden', 'boolean', default=False),
                Field('disabled', 'boolean', default=False),
                Field('pricebroken', 'boolean', default=False)
                )

PACK_JSON_GUIDE = """
JSON-formatted. Sample: 
{"587" : { "NAME" : "Rifter",
           "COUNT" : 5,
           "DISPLAY": "Render"},
 "11400": { "NAME" : "Jaguar",
            "COUNT" : 1,
            "DISPLAY" : "http://image.eveonline.com/Type/11770_64.png" }
}
"""
db.define_table('prize',
                Field('reel', db.reel, required=True),
                Field('name', required=True),
                Field('repeat', 'integer', required=True),
                Field('imgurl', required=True, comment="URL, or 'Type', or 'Render'"),
                Field('typeid'),
                Field('iskprize', 'double'),
                Field('pack', 'text', comment=PACK_JSON_GUIDE, required=True, default="")
                )

db.define_table('award',
                Field('char', db.char, required=True),
                Field('prize', db.prize, required=True),
                Field('date', 'datetime'),
                Field('givendate', 'datetime'),
                Field('agent', db.char),
                )

db.define_table('journal',
                Field('char', db.char, required=True),
                Field('amount', 'double'),
                Field('date', 'datetime'),
                Field('refid'),
                Field('comment'))

db.define_table('spin',
                Field('char', db.char, required=True),
                Field('reel', db.reel, required=True),
                Field('date', 'datetime', required=True),
                Field('award', db.award))

db.define_table('news',
                Field('title', required=True),
                Field('date', 'datetime', required=True),
                Field('body', 'text', required=True),
                Field('author', db.char, required=True),
                Field('editdate', 'datetime', default=None),
                Field('editauthor', db.char, default=None))

# Currently unused
db.define_table('comment',
                Field('body', 'text', required=True),
                Field('date', 'datetime', required=True),
                Field('author', db.char, required=True),
                Field('post', db.news, required=True))

db.define_table('credit_code',
                Field('name', required=True),
                Field('code', required=True, unique=True),
                Field('isk', 'double', required=True),
                Field('active', 'boolean', required=True, default=False))

db.define_table('claim',
                Field('char', db.char, required=True),
                Field('credit_code', db.credit_code, required=True),
                Field('date', 'datetime', required=True))
                
db.define_table('referral',
                Field('referrer', db.char, required=True),
                Field('recipient', db.char, required=True),
                Field('date', 'datetime', required=True),
                Field('claimed', 'boolean', required=True, default=False),
                )

db.define_table('price_cache',
                Field('typeid', required=True),
                Field('price', 'double', required=True),
                Field('date', 'datetime', required=True))

db.define_table('price_cache_sell',
                Field('typeid', required=True),
                Field('price', 'double', required=True),
                Field('date', 'datetime', required=True))

db.define_table('buyout',
                Field('award', db.award, required=True),
                Field('isk', 'double', required=True))

db.define_table('persist_vars',
                Field('key', required=True, unique=True),
                Field('value'))

db.define_table('attrib',
                Field('name', required=True))

db.define_table('attrib_value',
                Field('attrib', db.attrib, required=True),
                Field('name', required=True))

db.define_table('reel_metadata',
                Field('reel', db.reel, required=True),
                Field('attrib', db.attrib, required=True),
                Field('value', db.attrib_value, required=True))
