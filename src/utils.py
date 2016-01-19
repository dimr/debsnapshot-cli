import requests
import logging


BASE_URL = 'http://snapshot.debian.org/'
ALL_PACKAGES = BASE_URL+'mr/package/'
BINARY_URL = BASE_URL + 'binary/{binary}/'
ALL_FILES = BASE_URL + 'package/{binary}/{version}/allfiles'
INFO_HASH_URL = BASE_URL + "file/{hash}/info"

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logger = logging.getLogger('__apt-snapshot__')


def url_join(a, b):
    return requests.compat.urljoin(a, b)


class SnapConnection(object):
    def __init__(self, url):
        self.url = url
        # print('------', self.url)

    def __enter__(self):
        self.response = requests.get(self.url)
        self.response.raise_for_status()
        # print('----------->', self.url, self.response.ok)
        logger.debug('Requesting %s' % self.url)
        return self.response

    def __exit__(self, exc_type, exc_val, exc_tb):
        # print exc_type, exc_val, exc_tb
        if isinstance(exc_val, requests.exceptions.MissingSchema):
            return True
        logger.debug('Closing connection...')
        self.response.close()


def get_request_from_snapshot(url):
    with SnapConnection(url) as response:
        return response
