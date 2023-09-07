import logging
import re

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
        ):

        self.logger = self.__configure_logger
        self.tor_path = tor_path
        self.socks_port = socks_port
        self.tor_process = None
        self.session = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.__close()

    def __close(self):
        if self.tor_process and self.session:
            self.tor_process.kill()
            self.tor_process = None
            self.session.close()

    def __init_tor_process(self):
        self.tor_process = launch_tor_with_config(
            config={'SocksPort': str(self.socks_port)},
            init_msg_handler=self.__handle_bootstrap_message,
            tor_cmd=self.tor_path
        )
        self.session = self.__setup_session()

    def __handle_bootstrap_message(self, line):
        if 'Bootstrapped' in line:
            matches = re.search(r'\d+%.*\)', line)
            percentage = matches.group()
            if percentage is not None:
                print(f'TOR Progress - {term.format(percentage, term.Color.BLUE)}', end='\r')
            print(end='\033[K')

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

    def __get_ip_info(self, show_tor_ip=False):
        response = self.get(self.IP_URL) if show_tor_ip else requests.get(self.IP_URL)
        response_json = response.json()
        return {'ip': response_json['ip'], 'country': response_json['country']}

    @property
    def __configure_logger(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)

    @property
    def renew_tor_ip(self):
        self.logger.info(term.format('___Starting renewing IP___', term.Color.YELLOW))
        current_ip = self.__get_ip_info(show_tor_ip=True)
        self.__close()
        if not self.tor_process:
            self.__init_tor_process()
        new_ip = self.__get_ip_info(show_tor_ip=True)
        if new_ip['ip'] != current_ip['ip']:
            self.logger.info(term.format('___Renewing IP Succeed___', term.Color.YELLOW))
        else:
            raise IPRenewalError(term.format('Renewing IP failed!', term.Color.RED))

    @property
    def local_ip(self):
        local_ip = self.__get_ip_info()
        self.logger.info(term.format(f'Local IP: {local_ip["ip"]} [{local_ip["country"]}]', term.Color.GREEN))

    @property
    def tor_ip(self):
        local_ip = self.__get_ip_info()
        tor_ip = self.__get_ip_info(show_tor_ip=True)
        if local_ip['ip'] == tor_ip['ip']:
            raise IPProtectionError(term.format('Your IP is not protected!', term.Color.RED))
        self.logger.info(term.format(f'Tor IP: {tor_ip["ip"]} [{tor_ip["country"]}]', term.Color.GREEN))

    @property
    def checking_status(self):
        response = self.get(self.STATUS_URL)
        self.logger.info(
            term.format('Congratulations! Tor network is successfully configured.', term.Color.MAGENTA)
            if 'Congratulations' in response.text
            else term.format('Sorry! Failed to configure Tor network.', term.Color.RED)
        )

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
