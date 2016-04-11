def request_is_igb():
    return 'http_eve_trusted' in request.env

def request_is_trusted():
    return request.env['http_eve_trusted']=='Yes'

def request_is_proper():
    return request_is_igb() and request_is_trusted()
