import logging

import requests
from stem.process import launch_tor_with_config
from stem.util import term
from user_agent import generate_user_agent as UserAgent

from error import IPProtectionError, IPRenewalError


class TorService:
    IP_URL = 'https://ipwho.is/'
    STATUS_URL = 'https://check.torproject.org/'

    def __init__(
        self,
        tor_path=r'Tor\tor.exe',
        socks_port=9050,
        bootstrap=True,
        ):

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
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

        self.tor_process = launch_tor_with_config(
            config={'SocksPort': str(self.socks_port)},
            init_msg_handler=init_msg_handler,
            tor_cmd=self.tor_path
        )

    def __handle_bootstrap_message(self, line):
        if 'Bootstrapped' in line:
            self.logger.info(term.format(line, term.Color.BLUE))

    def __kill_tor_process(self):
        if self.tor_process:
            self.tor_process.kill()
            self.tor_process = None

    def __setup_session(self) -> requests.Session:
        session = requests.Session()
        session.headers = {'User-Agent': UserAgent()}
        session.proxies = {
            'http': f'socks5h://127.0.0.1:{self.socks_port}',
            'https': f'socks5h://127.0.0.1:{self.socks_port}'
        }
        return session

    def __make_request(self, method, url, **kwargs):
        if not self.tor_process:
            self.__init_tor_process()
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except requests.RequestException as e:
            self.logger.error(term.format(f'Request error: {e}', term.Color.RED))
            return None

    def renew_tor_ip(self):
        self.logger.info(term.format('___Starting renewing IP___', term.Color.YELLOW))
        current_ip = self.checking_ip(show_tor_ip=True)
        self.__kill_tor_process()
        if not self.tor_process:
            self.__init_tor_process()
        new_ip = self.checking_ip(show_tor_ip=True)
        if new_ip['ip'] != current_ip['ip']:
            self.logger.info(term.format('___Renewing IP Succeed___', term.Color.YELLOW))
        else:
            raise IPRenewalError(term.format('Renewing IP failed!', term.Color.RED))

    def checking_ip(self, show_tor_ip=False):
        response = requests.get(self.IP_URL)
        response_json = response.json()
        local_ip = {'ip': response_json['ip'], 'country': response_json['country']}

        if show_tor_ip:
            response = self.get(self.IP_URL)
            response_json = response.json()
            tor_ip = {'ip': response_json['ip'], 'country': response_json['country']}
            if local_ip['ip'] == tor_ip['ip']:
                raise IPProtectionError(term.format('Your IP is not protected!', term.Color.RED))
            return tor_ip
        else:
            return local_ip

    def checking_status(self):
        response = self.get(self.STATUS_URL)
        if 'Congratulations' in response.text:
            return term.format('Congratulations! Configured to use Tor.', term.Color.GREEN)
        else:
            return term.format('Sorry! You are not using Tor.', term.Color.RED)

    def get(self, url, **kwargs):
        return self.__make_request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self.__make_request('POST', url, **kwargs)

    def put(self, url, **kwargs):
        return self.__make_request('PUT', url, **kwargs)

    def head(self, url, **kwargs):
        return self.__make_request('HEAD', url, **kwargs)

    def options(self, url, **kwargs):
        return self.__make_request('OPTIONS', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.__make_request('DELETE', url, **kwargs)

    def patch(self, url, **kwargs):
        return self.__make_request('PATCH', url, **kwargs)

