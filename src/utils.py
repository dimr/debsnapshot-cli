import requests
import logging
import sys
from pkg_resources import get_distribution, DistributionNotFound
from __init__ import __version__, __title__

BASE_URL = 'http://snapshot.debian.org/'
ALL_PACKAGES = BASE_URL + 'mr/package/'
BINARY_URL = BASE_URL + 'binary/{binary}/'
ALL_FILES = BASE_URL + 'package/{binary}/{version}/allfiles'
INFO_HASH_URL = BASE_URL + "file/{hash}/info"

DEBIAN_PORTS = ['amd64', 'armel', 'armhf', 'i386', 'ia64', 'kfreebsd-amd64', 'kfreebsd-i386', 'mips', 'mipsel',
                'powerpc', 'ppc64el',
                's390', 'sparc']

logging.basicConfig(level=logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logger = logging.getLogger('__apt-snapshot__')


def url_join(a, b):
    return requests.compat.urljoin(a, b)


class SnapConnection(object):
    def __init__(self, url):
        self.url = url
        # but why needs strip()?
        self.headers = {'User-Agent': " : ".join((__title__, __version__))}

    def __enter__(self):
        try:
            self.response = requests.get(self.url, headers=self.headers)
            # print self.response.request.headers
        except KeyboardInterrupt:
            logger.debug("\nBye")
        except requests.exceptions.ConnectionError:
            logger.error("Not internet connection")
            sys.exit()
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


def snapshot_get(url, ):
    with SnapConnection(url) as response:
        return response


def check_port(architecture):
    if architecture in DEBIAN_PORTS:
        return architecture
    raise ValueError('No such debian port : {port}'.format(port=architecture))
