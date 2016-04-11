
def default_menu():
    menu = [ ['News', False, URL('general','news')],
             #['Stations', False, URL('spin','reels')],
             #['My Character', False, URL('char','index')],
             ['Winners', False, URL('char','allwins')],
             ['FAQ', False, URL('general','faq')] ]

    if user_is_agent():
        menu.append(['Agent', False, URL('agent','give_prizes')])
    
    return menu

DOMAIN_NAME = "shipspinning.com"
DOMAIN_URL = "http://shipspinning.com"
