from json import dumps
from services import TorService


bootstrap = True # Set False if you dont want to print bootstrap message

with TorService(bootstrap=bootstrap) as tor:
    print(f'\nLocal IP: {tor.checking_ip(show_tor_ip=False)}\n')
    print(f'\nTor IP: {tor.checking_ip()}\n')

    #! Renewing IP
    tor.renew_tor_ip()
    print(f'\nTor IP: {tor.checking_ip()}\n')

    result = {}

    #! GET Request
    response_get = tor.get('https://httpbin.org/get')
    result['GET'] = response_get.json()

    #! GET Request with Query Parameters
    query_params = {'param1': 'value1', 'param2': 'value2'}
    response_query = tor.get('https://httpbin.org/get', params=query_params)
    result['QUERY'] = response_query.json()

    #! POST Request
    data = {'key': 'value'}
    response_post = tor.post('https://httpbin.org/post', json=data)
    result['POST'] = response_post.json()

    #! PUT Request
    data = {'updated_key': 'updated_value'}
    response_put = tor.put('https://httpbin.org/put', json=data)
    result['PUT'] = response_put.json()
    
    #! HEAD Request
    response_head = tor.head('https://httpbin.org/get')
    result['HEAD'] = dict(response_head.headers)

    #! OPTIONS Request
    response_options = tor.options("https://httpbin.org")
    result['OPTIONS'] = dict(response_options.headers)

    #! DELETE Request
    response_delete = tor.delete('https://httpbin.org/delete')
    result['DELETE'] = response_delete.json()

    #! Testing ONION URL (Facebook onion from https://www.expressvpn.com/blog/best-onion-sites-on-dark-web/)
    response_onion = tor.get('https://www.facebookwkhpilnemxj7asaniu7vnjjbiltxjqhye3mhbshg7kx5tfyd.onion/')
    result['ONION'] = dict(response_onion.headers)

    print(dumps(result, indent=4))
