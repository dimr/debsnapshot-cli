from utils import SnapConnection
from utils import get_request_from_snapshot, url_join
from utils import BASE_URL, ALL_PACKAGES
import requests


def get_all_packages():
    with SnapConnection(url_join(BASE_URL, ALL_PACKAGES)) as response:
        return response


class SnapshotRequest(object):
    def __init__(self, package_name, architecture=None):
        self.package_name = package_name
        self.session = requests.Session()

    def session_get(self, url):
        response = self.session.get(url)
        response.raise_for_status()
        return response

    def close(self):
        self.session.close()

    def list_all_available_source_versions(self):
        """
        URL: /mr/package/<package>/
        http status codes: 200 500 404 304
        summary: list all available source versions for this package
        :return: list
        """
        response = self.session_get(url_join(BASE_URL, '/mr/package/{package}/'.format(package=self.package_name)))
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
        response = self.session_get(url)
        return [str(h['hash']) for h in response.json()['result']]

    def list_all_binary_packages_for_this_package_at_version(self, version):
        """
        URL: /mr/package/<package>/<version>/binpackages
        http status codes: 200 500 404 304
        summary: list all binary packages associated with this source package at that version
        :param version:
        :return: **temporary** return dict
        """
        url = url_join(BASE_URL, 'mr/package/{package}/{version}/binpackages'.format(package=self.package_name, version=version))
        response = self.session_get(url)
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
        response = self.session_get(url)
        return response.json()

    def list_all_files_associated_with_this_source_package_at_that_version(self, version):
        """
        URL: /mr/package/<package>/<version>/allfiles
        Options: fileinfo=1  includes fileinfo section
        http status codes: 200 500 404 304
        summary: list all files associated with this source package at that version
        :param version: the version of the package
        :return:
        """
        url = url_join(BASE_URL, '/mr/package/{package}/{version}/allfiles'.format(package=self.package_name, version=version))
        response = self.session_get(url)
        return response.json()

    def find_binary_package_versions_and_corresponding_source_names_and_versions(self, binary):
        """
        URL: /mr/binary/<binary>/
        http status codes: 200 500 404 304
        summary: find binary package versions and corresponding source names and versions
        :param binary: binary package name
        :return:
        """
        url = url_join(BASE_URL, '/mr/binary/{binary}/'.format(binary=self.package_name))
        response = self.session_get(url)
        return [str(b_version['binary_version']) for b_version in response.json()['result']]

    def info_from_hash(self, the_hash):
        """
        URL: /mr/file/<hash>/info
        http status codes: 200 500 404 304
        :param hash:
        :return:
        """
        url = url_join(BASE_URL, '/mr/file/{the_hash}/info'.format(the_hash=the_hash))
        response = self.session_get(url)
        return response.json()
