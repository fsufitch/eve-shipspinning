import hashlib, random

def get_referral_code(charid):
    """ Lazily generate a refcode for a character. """
    char = get_char_row_from_id(charid)
    refcode = char.refcode
    if not refcode:
        chars = list(hashlib.md5(char.charname).hexdigest())
        random.shuffle(chars)
        refcode = ''.join(chars[:10])
        db(db.char.charid == charid).update(refcode=refcode)
        db.commit()

    return refcode

def get_uncashed_referrals(char):
    """ Return how many cashable referrals this character has. """
    refs = db((db.referral.referrer==char) & (db.referral.claimed==False)).select()
    count = 0
    for row in refs:
        if total_donated_by(row.recipient) > 1000000:
            count += 1
    return count

def cash_referrals(char):
    """ Cash in all referrals of charid. """
    PER_REFERRAL = 1000000
    q = db((db.referral.referrer==char) & (db.referral.claimed==False))
    addisk = PER_REFERRAL * get_uncashed_referrals(char)
    if not addisk > 1:
        return
    newisk = char.isk + addisk
    char.update_record(isk=newisk)
    db.journal.insert(char=char, amount=addisk, date=get_time(), refid=None, comment="Referral reward")
    q.update(claimed=True)
    db.commit()

def get_claimed_referrals(char):
    """ Return how many claimed referrals this character has. """
    return db((db.referral.referrer==char) & (db.referral.claimed==True)).count()


REF_PRIZE_TIERS = {
    0: {
        "numrefs": 5,
        "isk": 10000000,
        "bonus": 0,
        "extra": None,
        },
    1: {
        "numrefs": 10,
        "isk": 25000000,
        "bonus": 0,
        "extra": None,
        },
    2: {
        "numrefs": 30,
        "isk": 100000000,
        "bonus": 0,
        "extra": None,
        },
    3: {
        "numrefs": 50,
        "isk": 100000000,
        "bonus": 0,
        "extra": "Featured on front page!",
        },
    4: {
        "numrefs": 100,
        "isk": 0,
        "bonus": 0.075,
        "extra": None,
        },
    5: {
        "numrefs": 200,
        "isk": 500000000,
        "bonus": 0,
        "extra": "Design your own ship spinning station!",
        },
}

def get_referral_prizes(char):
    claimed = char.ref_bonuses_used if char.ref_bonuses_used else []
    num_claimed = get_claimed_referrals(char)
    claimable = []
    not_claimable = []
    for k in REF_PRIZE_TIERS:
        if k in claimed:
            continue
        if num_claimed >= REF_PRIZE_TIERS[k]["numrefs"]:
            claimable.append(k)
        else:
            not_claimable.append(k)

    return claimed, claimable, not_claimable

def claim_referral_prize(char, prize_id):
    num_claimed = get_claimed_referrals(char)
    prize_id = int(prize_id)
    if num_claimed < REF_PRIZE_TIERS[prize_id]["numrefs"]:
        return "not enough referrals"
    claimed = char.ref_bonuses_used if char.ref_bonuses_used else []
    if prize_id in claimed:
        return "already claimed"
    prize = REF_PRIZE_TIERS[prize_id]
    commit = False
    if prize["isk"]:
        newisk = char.isk + prize["isk"]
        comment = "Referral bonus prize for %s referrals" % prize["numrefs"]
        db.journal.insert(char=char, amount=prize["isk"], date=get_time(), refid=None, comment=comment)        
        char.update_record(isk=newisk)
        commit = True
    if prize["bonus"] and prize["bonus"] > char.bonus_mult:
        char.update_record(bonus_mult=prize["bonus"])
        commit = True
    
    if commit:
        if not char.ref_bonuses_used:
            char.update_record(ref_bonuses_used=[prize_id])
        else:
            char.update_record(ref_bonuses_used=char.ref_bonuses_used+[prize_id])
        db.commit()

    return prize_id
