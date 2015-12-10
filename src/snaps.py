import requests, apt
import sys, os, logging
from datetime import datetime
from collections import namedtuple


def handle_interrupt(func):
    def wrap():
        try:
            func()
        except KeyboardInterrupt:
            print '\nBye!'
            sys.exit()

    return wrap()


logging.basicConfig(level=logging.INFO)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logger = logging.getLogger('__apt-snapshot__')
# logger.propagate = False

BASE_URL = 'http://snapshot.debian.org/mr/'
BINARY_URL = BASE_URL + 'binary/{binary}/'
ALL_FILES = BASE_URL + 'package/{binary}/{version}/allfiles'
INFO_HASH_URL = BASE_URL + "file/{hash}/info"


class PackageParser(object):
    def __init__(self, package_name, version=None):
        # print args,type(args)
        self.cache = apt.Cache()
        self.package_name = package_name
        logger.debug('Picked:%s' % self.package_name)
        try:
            self.package = self.cache[package_name.strip().lower()]
            self.package_name = self.package.name
            self.package_full_name = self.package.fullname
        except (KeyError, AttributeError):
            # print "no Such package in cache: ", self.package_name

            logger.warning("no Such package in cache: {package}".format(package=self.package_name))
            sys.exit()
        self.__join = lambda a, b: requests.compat.urljoin(a, b)
        self.response = None
        try:
            self.response = requests.get(self.__join(BASE_URL, BINARY_URL.format(binary=self.package_name)), timeout=(10, 10))
        except requests.exceptions.ConnectTimeout as e:
            logger.warning('TIMED OUT')
            sys.exit()
        except requests.exceptions.ConnectionError as e:
            logger.warning("CONNECTION ERROR")
            sys.exit()
        # except requests.exceptions.RequestException as e:
        # print "SDFSD"
        # sys.exit()
        logger.debug("initial request response status:%d" % self.response.status_code)
        logger.debug("closing connection")
        # print '--------',self.response.elapsed.total_seconds()

        if not self.response:
            # print self.response.status_code, "not installed from official debian repository"
            logger.warning(self.package_name + ' not installed from official debian repository')
            sys.exit()
            # self.__binary_versions = None
        self._target_hash = ''
        self._all_binary_versions = [str(version['binary_version']) for version in self.response.json()['result']]
        self._previous_version = None
        try:
            package_list_length = len(self.all_binary_versions)
            if package_list_length != 1:
                self._previous_version = self.all_binary_versions[self.all_binary_versions.index(self.installed_version) + 1]
            elif package_list_length == 1:
                logger.warning("Only one package available {package}".format(package=self.package_name))
                self._previous_version = self.all_binary_versions[self.all_binary_versions.index(self.installed_version)]
                # print(self.installed_version)
                # print(self.previous_version)
        except (ValueError, AttributeError) as e:
            print "CANNOT"
            print e
        # print(self.system_arch)
        # print(self.is_installed)
        # print(self.is_latest)
        self._target_version = None
        # print(self.all_binary_versions)
        # print(self.previous_version)
        if version is None:
            self.target_version = ''

    @property
    def system_arch(self):
        libc6_arch = self.cache['libc6'].architecture()
        if not self.is_installed:
            #logger.warning("{package} is not installed, getting system arch from libc6".format(package=self.package.name))
            return libc6_arch
        arch = self.cache[self.package].architecture()
        assert (arch == libc6_arch), 'Problem with system architectures -> {package}={local_arch} , libc6={libc6_arch}'.format(package=self.package_name, local_arch=arch,
                                                                                                                               libc6_arch=libc6_arch)
        return arch

    @property
    def is_installed(self):
        return self.cache[self.package].is_installed

    @property
    def installed_version(self):
        '''
        if package NOT installed self.package_name.installed is None
        :return:
        '''
        if not self.is_installed:
            # print "NO INSTALLED"
            logger.warning("Package {package} is not installed".format(package=self.package_name))
            return None
        return self.package.installed.version

    @property
    def archive(self):
        return self.package_name.installed.origins[0].archive

    @property
    def origin(self):
        logger.debug('installed from %s' % self.package_name.installed.origins[0].origin)
        return self.package_name.installed.origins[0].origin

    @property
    def all_binary_versions(self):
        # here version works in most packages, binary_version does not
        return self._all_binary_versions

    @all_binary_versions.setter
    def all_binary_versions(self, b):
        self._all_binary_versions = b

    @property
    def is_latest(self):
        if self.is_installed:
            return True if apt.apt_pkg.version_compare(self.all_binary_versions[0], self.installed_version) == 0 else False
        print("NOT INSTALLED")
        return False

    @property
    def previous_version(self):
        return self._previous_version

    @previous_version.setter
    def previous_version(self, p_v):
        if not self.is_installed:
            self._previous_version = None
            logger.warning("SETTING PREVIOUS VERSION TO None")
            return
        if len(self.all_binary_versions) == 1:  # peasytray
            logger.warning("only one version available {version}".format(version=self.installed_version))
            # setting previous version equal to installed version (for now)
            self._previous_version = self.installed_version
        self._previous_version = p_v
        # if len(self.all_binary_versions) == 1:  # pasystray
        #     logger.warning("only one version available {version}".format(version=self.installed_version))
        #     sys.exit()
        # logger.debug("picking previous version")
        # try:
        #     self._previous_version = self.all_binary_versions[self.all_binary_versions.index(self.installed_version) + 1]
        # except Exception:
        #     pass

    @property
    def target_version(self):
        try:
            return self._target_version
        except AttributeError:
            logger.warning("target version has not yet been set")

    @target_version.setter
    def target_version(self, version):
        loc_version = None
        if version == '':
            logger.error("Have not set target version yet\n Settings target version = previous version")
            print(self.previous_version)
            self._target_version = self.previous_version
        if version in self.all_binary_versions:
            #logger.info('PACKAGE FOUND')
            try:
                self._target_version = self.all_binary_versions[self.all_binary_versions.index(version)]
                # logger.info("requests version {version}".format(version=version))
            except ValueError:
                logger.error("not such package version {package}:{version}".format(package=self.package_name, version=version))

    @property
    def target_version_hash(self):
        '''URL: /mr/package/<package>/<version>/allfiles
        '''

        r = requests.get(self.__join(BASE_URL, ALL_FILES.format(binary=self.package_name, version=self.target_version)))
        # try:
        # r.raise_for_status()
        # except requests.exceptions.HTTPError as e:

        # print self.__join(BASE_URL, ALL_BINARIES_URL.format(binary=self.package_name.name, version=self._target_version))
        # print r.status_code
        if r:
            for i in r.json()['result']['binaries']:
                if i['name'] == self.package_name and i['version'] == self.target_version:
                    for j in i['files']:
                        if j['architecture'] == self.system_arch:
                            logger.debug("found architecture {arch}".format(arch=j['architecture']))
                            self._target_hash = j['hash']
                            return j['hash']
                        elif j['architecture'] == 'all':
                            logger.debug("Not specific architectures, picking all")
                            self._target_hash = j['hash']
                            return j['hash']

    @property
    def target_first_seen(self):
        logger.debug("quering first seen")
        r = requests.get(self.__join(BASE_URL, INFO_HASH_URL.format(hash=self.target_version_hash)))
        logger.debug("closing connection status_code:{code}".format(code=r.status_code))
        r.close()
        if r.status_code == 404:
            logger.debug("it does not exists")
            #sys.exit()
            return "404"
        if r:
            return r.json()['result'][0]['first_seen']

    def __str__(self):
        return "Package name: " + self.package_name + ", Installed Version: " + str(self.installed_version) \
               + " is Latest: " + str(self.is_latest) + " Previous Version: " + str(self.previous_version) + \
               " Target Version: " + str(self.target_version) + " First seen: " + str(self.target_first_seen)


if __name__ == '__main__':

    pack = 'meshlab'

    if len(sys.argv) == 1:
        p = PackageParser(pack)
        print p.all_binary_versions
        for version in p.all_binary_versions:
            p.target_version = version
            logger.info(p.target_version + " " + str(p.target_first_seen) + " " + str(p.target_version_hash))
        # p.target_version = '1:6.4+7.0g01-1'
        # print p.target_version
        # print p.target_version_hash
        # print p.target_first_seen
        print p
        # for i in p.all_binary_versions:
        #     print i
            # print p.latest
    else:
        p = PackageParser(sys.argv[1], )
        print p.all_binary_versions
        for version in p.all_binary_versions:
            p.target_version = version
            logger.info(p.target_version + " " + str(p.target_first_seen) + " " + str(p.target_version_hash))
        print p
    # print p.all_binary_versions
    # print p.installed_version
    # print p.previous_version
    import re

    print("\n")
    # try:
    #     logger.info("Number of packages {number}:".format(number=len(p.all_binary_versions)) + "\n")
    #     for i in p.all_binary_versions:
    #         p.target_version=i
    #         logger.info(i)
    #         # for i, version in enumerate(p.all_binary_versions):
    #         #
    #         #     logger.info(str(i) + " " + version + " " +version.target_first_seen)
    #         #     #
    #         # if not re.search('b[0-9]{1}$', version):
    #         #     p.target_version = version
    #         #     # logger.debug(i,version, p.target_version_hash,p.target_first_seen)#
    #         #     logger.info(" " + str(i) + "  " + str(version) + " " + str(p._target_hash) + " " + str(p.target_first_seen))
    #         # else:
    #         #     logger.warning(" " + str(i) + " " + str(version) + " " + str(version))
    #
    #
    #
    # except AttributeError:
    #     # p.target_version='2.20-3'
    #     # print p.target_version_hash
    #     # print p.target_first_seen
    #     #
    #
    #
    #     # print p.all_binary_versions
    #     # print p.previous_version
    #     # print p.latest, p.origin
    #     # p.target_version = p.previous_version
    #     # print p, p.target_hash, p.target_first_seen
    #     # print p.target_hash, p.target_first_seen,datetime.strptime(p.target_first_seen, "%Y%m%dT%H%M%SZ")
    #     # print datetime.strptime(p.target_first_seen, "%Y%m%dT%H%M%SZ")
    #     #
    #     # data=[]
    #     # f=open('desktop.txt','r')
    #     # the_line=f.readline()
    #     # while the_line!='':
    #     # data.append(the_line.split(' ')[2][:-1])
    #     # the_line=f.readline()
    #     #
    #     # #print data[0].split(' ')[2]
    #     # for i in data:
    #     #
    #     # p=PackageParser(i)
    #     # p.target_version = p.previous_version
    #     # print i,p.target_first_seen
    #
    #     # failed: ipython(all),terminator(all),gpick(?),gthumb
    #     print "DOWN HERE"
