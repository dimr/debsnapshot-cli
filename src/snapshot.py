from utils import SnapConnection
from utils import url_join, snapshot_get
from utils import BASE_URL, ALL_PACKAGES, DEFAULT_TIMEOUT
import requests
import logging

logging.basicConfig(level=logging.CRITICAL)
# logging.getLogger("requests").setLevel(logging.CRITICAL)
logger = logging.getLogger('__debsnapshot-cli__')


def get_all_packages():
    with SnapConnection(url_join(BASE_URL, ALL_PACKAGES)) as response:
        return response


class SnapshotRequest(object):
    def __init__(self, package_name, timeout=DEFAULT_TIMEOUT):
        self.loggerA = logging.getLogger(self.__class__.__name__)
        #  logger = logging.getLogger(self.__class__.__name__)
        self.package_name = package_name
        # self.kwargs=kwargs
        # print '>?>?', self.kwargs
        # # self.session = requests.Session()
        self.timeout = timeout
        url = url_join(BASE_URL, '/mr/binary/{binary}/'.format(binary=self.package_name))
        self.initial_response = snapshot_get(url, self.timeout).json()
        # self.initial_response = self.find_binary_package_versions_and_corresponding_source_names_and_versions(self.package_name)
        self.source_name = self.initial_response['result'][0]['source']
        self.binary_name = self.initial_response['result'][0]['name']
        self.loggerA.debug('\nsource_name:{s},\nbinary_name:{b}\npackage_name:{p}\n'.format(s=self.source_name, b=self.binary_name, p=self.package_name))
        # assert r['result'][0]['name'] == r['result'][0]['source'], 'NOT THE SAME \nsource_name:{s},\nbinary_name:{b}\npackage_name:{p}'.format(s=self.source_name, b=self.binary_name,p=self.package_name)

    def general_info(self):
        l = [i['source'] for i in self.initial_response['result']]
        result = {}
        result['Source name(s)'] = list(set([str(i['source']) for i in self.initial_response['result']]))
        result['Binary name'] = list(set([i['name'] for i in self.initial_response['result']]))
        # print 'Source name(s): ', list(set([str(i['source']) for i in self.initial_response['result']]))
        # print 'Binary name: ', list(set([i['name'] for i in self.initial_response['result']]))
        return result

    def list_all_available_source_versions(self):
        """
        URL: /mr/package/<package>/
        http status codes: 200 500 404 304
        summary: list all available source versions for this package
        :return: list
        """
        try:
            response = snapshot_get(url_join(BASE_URL, '/mr/package/{package}/'.format(package=self.package_name)), self.timeout)
        except requests.exceptions.HTTPError:
            # print 'NNNNNNNNNNNNNNNNNNB'
            self.loggerA.debug(
                'Making request with source_name:{source_name} instead of package_name:{package_name}'.format(source_name=self.source_name, package_name=self.package_name))
            response = snapshot_get(url_join(BASE_URL, '/mr/package/{package}/'.format(package=self.source_name)), self.timeout)
        return [str(version['version']) for version in response.json()['result']]

    def list_all_sources_for_this_package_at_version(self, version):
        """
        URL: /mr/package/<package>/<version>/srcfiles
        Options: fileinfo=1  includes fileinfo section
        http status codes: 200 500 404 304
        summary: list all source files associated with this package at that version
        :param version: the version of the package
        :return: list of hashes
        """
        url = url_join(BASE_URL, 'mr/package/{package}/{version}/srcfiles'.format(package=self.package_name, version=version))
        try:
            response = snapshot_get(url, self.timeout)
        except requests.exceptions.HTTPError:
            url = url_join(BASE_URL, 'mr/package/{package}/{version}/srcfiles'.format(package=self.source_name, version=version))
            response = snapshot_get(url, self.timeout)

        # return [str(h['hash']) for h in response.json()['result']]
        return response.json()

    def list_all_binary_packages_for_this_package_at_version(self, version):
        """
        URL: /mr/package/<package>/<version>/binpackages
        http status codes: 200 500 404 304
        summary: list all binary packages associated with this source package at that version
        :param version:
        :return: **temporary** return dict
        """
        url = url_join(BASE_URL, 'mr/package/{package}/{version}/binpackages'.format(package=self.package_name, version=version))
        try:
            response = snapshot_get(url, self.timeout)
        except  requests.exceptions.HTTPError:
            url = url_join(BASE_URL, 'mr/package/{package}/{version}/binpackages'.format(package=self.source_name, version=version))
            response = snapshot_get(url, self.timeout)
        return response.json()['result']

    def list_all_files_associated_with_a_binary_package(self, version, binpkg, binversion):
        """
        URL: /mr/package/<package>/<version>/binfiles/<binpkg>/<binversion>
        Options: fileinfo=1  includes fileinfo section
        http status codes: 200 500 404 304
        summary: list all files associated with a binary package
        :param version: the version of binpkg
        :param binpkg: binpackage you get from list_all_binary_packages_for_this_package_at_version(self, version)
        :param binversion: version of **binpkg**
        :return:
        """
        url = url_join(BASE_URL,
                       '/mr/package/{package}/{version}/binfiles/{binpkg}/{binversion}'.format(package=self.package_name, version=version, binpkg=binpkg, binversion=binversion))
        response = snapshot_get(url, self.timeout)
        return response.json()

    def target_version_hash(self, r, version, arch=None):
        '''URL: /mr/package/<package>/<version>/allfiles
        '''
        if r:
            for i in r.json()['result']['binaries']:
                if i['name'] == self.package_name and i['version'] == version:
                    for j in i['files']:
                        if j['architecture'] == arch:
                            return j['hash']
                        elif j['architecture'] == 'all':
                            return j['hash']

    def list_all_files_associated_with_this_source_package_at_that_version(self, version, arch=None):
        """
        URL: /mr/package/<package>/<version>/allfiles
        Options: fileinfo=1  includes fileinfo section
        http status codes: 200 500 404 304
        summary: list all files associated with this source package at that version
        :param version: the version of the package
        :return:
        """
        url = url_join(BASE_URL, '/mr/package/{package}/{version}/allfiles'.format(package=self.package_name, version=version))
        response = snapshot_get(url, self.timeout)
        return response.json()['result']

    def find_binary_package_versions_and_corresponding_source_names_and_versions(self, binary):
        """
        URL: /mr/binary/<binary>/
        http status codes: 200 500 404 304
        summary: find binary package versions and corresponding source names and versions
        :param binary: binary package name
        :return:
        """
        # url = url_join(BASE_URL, '/mr/binary/{binary}/'.format(binary=self.package_name))
        # response = snapshot_get(url)
        # assert response.json()['result'][0]['name']==response.json()['result'][0]['source']
        # return [str(b_version['binary_version']) for b_version in response.json()['result']]
        # return response.json()
        return self.initial_response

    def info_from_hash(self, version, arch=None):
        """
        URL: /mr/file/<hash>/info
        http status codes: 200 500 404 304
        :param hash:
        :return:
        """
        try:
            url = url_join(BASE_URL, '/mr/package/{package}/{version}/allfiles'.format(package=self.package_name, version=version))
            response = snapshot_get(url, self.timeout)
        except requests.exceptions.HTTPError:
            url = url_join(BASE_URL, '/mr/package/{package}/{version}/allfiles'.format(package=self.source_name, version=version))
            response = snapshot_get(url, self.timeout)
        the_hash = self.target_version_hash(response, version, arch)
        url = url_join(BASE_URL, '/mr/file/{the_hash}/info'.format(the_hash=the_hash))
        response = snapshot_get(url, self.timeout)
        return response.json()
