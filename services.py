import logging
import re

import requests
import stem.process


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IPRenewalError(Exception):
    pass

class IPProtectionError(Exception):
    pass


class TorService:
    IP_URL = 'https://ipwho.is/'

    def __init__(
        self,
        tor_path=r'Tor\tor.exe',
        socks_port=9050,
        bootstrap=True
        ):

        self.bootstrap = bootstrap
        self.tor_path = tor_path
        self.socks_port = socks_port
        self.tor_process = None
        self.session = self.__setup_session()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.__close()

    def __close(self):
        self.__kill_tor_process()

    def __init_tor_process(self):
        if self.bootstrap:
            init_msg_handler = self.__handle_bootstrap_message
        else:
            init_msg_handler = None

        self.tor_process = stem.process.launch_tor_with_config(
            config={'SocksPort': str(self.socks_port)},
            init_msg_handler=init_msg_handler,
            tor_cmd=self.tor_path
        )

    def __handle_bootstrap_message(self, line):
        if re.search('Bootstrapped', line):
            logging.info(line)

    def __kill_tor_process(self):
        if self.tor_process:
            self.tor_process.kill()
            self.tor_process = None

    def __setup_session(self) -> requests.Session:
        session = requests.Session()
        session.proxies = {
            'http': f'socks5://127.0.0.1:{self.socks_port}',
            'https': f'socks5://127.0.0.1:{self.socks_port}'
        }
        return session

    def __make_request(self, method, url, **kwargs):
        if not self.tor_process:
            self.__init_tor_process()
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except requests.RequestException as e:
            logging.error(f'Request error: {e}')
            return None

    def renew_tor_ip(self):
        logging.info('___Starting renewing IP___')
        current_ip = self.checking_ip()
        self.__kill_tor_process()
        self.__init_tor_process()
        new_ip = self.checking_ip()
        if new_ip['ip'] != current_ip['ip']:
            logging.info('___Renewing IP Succeed___')
        else:
            raise IPRenewalError('Renewing IP failed!')

    def checking_ip(self, show_tor_ip=True):
        response = requests.get(self.IP_URL)
        response_json = response.json()
        local_ip = {'ip': response_json['ip'], 'country': response_json['country']}

        if show_tor_ip:
            response = self.get(self.IP_URL)
            response_json = response.json()
            tor_ip = {'ip': response_json['ip'], 'country': response_json['country']}
            if local_ip['ip'] == tor_ip['ip']:
                raise IPProtectionError('Your IP is not protected!')
            return tor_ip
        else:
            return local_ip

    def get(self, url, **kwargs):
        return self.__make_request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self.__make_request('POST', url, **kwargs)

    def put(self, url, **kwargs):
        return self.__make_request('PUT', url, **kwargs)

    def options(self, url, **kwargs):
        return self.__make_request('OPTIONS', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.__make_request('DELETE', url, **kwargs)
