<div align="center">

<img src="https://github.com/x404xx/Py-Tor/assets/114883816/399cd3df-9b18-41b7-be20-29691f9dbf9a" width="300">

**Py-Tor** provides a simple and convenient way to interact with the Tor network, offering functionalities to renew IP addresses and ensure IP protection. This Python code demonstrates how to utilize the `stem` and `requests` libraries to achieve these tasks.

</div>

## Prerequisites

-   [Python](https://www.python.org/) (version 3.6 or higher)
-   [Stem Library](https://stem.torproject.org/) (to interact with Tor programmatically)
-   [Requests Library](https://docs.python-requests.org/en/latest/) (to make HTTP requests)

## Installation

To use _**Py-Tor**_, open your terminal and navigate to the folder that contains _**Py-Tor**_ content ::

```bash
pip install -r requirements.txt
```

## Example

```python
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

    #! GET Requests
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

    #! OPTIONS Request
    response_options = tor.options("https://httpbin.org")
    result['OPTIONS'] = dict(response_options.headers)

    #! DELETE Request
    response_delete = tor.delete('https://httpbin.org/delete')
    result['DELETE'] = response_delete.json()

    print(dumps(result, indent=4))
```

## **Note**

-   It's important to ensure that the path to the Tor executable (tor_path) is accurate for your system or just use the default.
-   This code does not handle Tor updates, potential network errors, or security considerations in a comprehensive manner. It's intended as a basic example to demonstrate the core functionality of interacting with Tor programmatically.

## **Legal Disclaimer**

> This was made for educational purposes only, nobody which directly involved in this project is responsible for any damages caused. **_You are responsible for your actions._**
