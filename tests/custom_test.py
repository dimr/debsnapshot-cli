from __future__ import absolute_import
import subprocess
import sys
import os
import unittest
import responses

sys.path.append(os.path.join('..', 'src'))

from snapshot import SnapshotRequest
import utils
import random
import requests

SNAPSHOT_URL = 'deb http://snapshot.debian.org/archive/debian/{time_stamp} unstable main'


def get_native_version(package, ask_for="Installed"):
    if ask_for == "Installed":
        return \
            subprocess.Popen(["apt-cache policy {package}".format(package=package)], stdout=subprocess.PIPE, shell=True).communicate()[0].split("\n")[1].lstrip().split(
                ask_for + ":")[
                1].strip()
    elif ask_for == "Candidate":
        return \
            subprocess.Popen(["apt-cache policy {package}".format(package=package)], stdout=subprocess.PIPE, shell=True).communicate()[0].split("\n")[2].lstrip().split(
                ask_for + ":")[
                1].strip()
    elif ask_for is None:
        return subprocess.Popen(["apt-cache policy {package}".format(package=package)], stdout=subprocess.PIPE, shell=True).communicate()[0]


# print('----')
# print get_native_version('inkscape')
# print get_native_version('inkscape',ask_for="Candidate")

class VersionParser(object):
    def __init__(self, package_name):
        self.package_name = package_name
        self.installed_version = "Installed"
        self.candidate_version = "Candidate"
        self.second_candidate = []
        self._parse_rest()
        # print '---', self.second_installed, self.second_candidate
        # assert (self.installed_version == self.second_installed), "Wrong Installed version"
        # assert (self.candidate_version in self.second_candidate), "Wrong Candidate Version {first}!={second}".format(first=self.candidate_version, second=self.second_candidate)

    def _parse_rest(self):
        out = get_native_version(self.package_name, ask_for=None)
        start = ([i.strip() for i in out.split("\n")].index("Version table:")) + 1
        sublist = out.split("\n")[start:]

        for i, line in enumerate(sublist):
            line = line.strip()
            version = ''
            url = ''
            if 'http' not in line and 'ftp' not in line and 'var/lib' not in line and line != '':
                # print  sublist[i+1]
                temp = sublist[i + 1].split(" ")
                # print [i for i in temp if 'http' in i]
                url = " ".join(filter(None, temp)[1:])
                version = ''.join(line.split(" ")[:-1])
                if version.startswith('***'):
                    self.second_installed = version[3:]
                    self.second_candidate.append(self.installed_version)
                else:
                    self.second_candidate.append(version)
                    # print (url, version)
                    # print '->', self.second_candidate
        print '------->', self.second_candidate

    @property
    def all_candidates(self):
        return self.second_candidate

    @property
    def installed_version(self):
        return self.__installed_version

    @installed_version.setter
    def installed_version(self, ask_for):
        self.__installed_version = get_native_version(self.package_name, ask_for)

    def get_candidates(self):
        return self.second_candidate

    def __str__(self):
        return 'Installed:' + self.installed_version + "\nCandidate:" + self.candidate_version + \
               "\nInstalled Check:" + self.second_installed + "\nCandidate Check:" + " , ".join([i for i in self.second_candidate])


# print len(sys.argv)
# if len(sys.argv) == 1:
#     v = VersionParser('nvidia-driver')
# elif len(sys.argv) == 2:
#     v = VersionParser(sys.argv[1])
# print v

def update():
    print('Updating....')
    os.system(
        'echo normaluser|sudo  -S apt-get -o  Dir::Etc::sourcelist="sources.list.d/snapshot.list" -o Dir::Etc::sourceparts="-" -o APT::Get::List-Cleanup="0"  -o Acquire::Check-Valid-Until=false update -qq')
    print ('Finished')


class PakcageTest(unittest.TestCase):
    p = 'lvm2'

    def test_package_parser(self):
        r = SnapshotRequest(self.p)
        self.assertIsNotNone(r)

    def test_Version(self):
        v = VersionParser(self.p)
        print v.candidate_version
        self.assertIsNotNone(v)

    # @responses.activate
    # def test_request(self):
    #     responses.add(responses.GET, utils.BASE_URL + utils.BINARY_URL.format(binary=self.p), status=400)
    #     resp = requests.get(utils.BASE_URL + utils.BINARY_URL.format(binary=self.p))
    #     assert resp.json()=={"error":"not found"}

    def test_upgrade(self):
        d_package = SnapshotRequest(self.p)
        all_versions = d_package.list_all_available_source_versions()
        random_version = random.randint(0, len(all_versions) - 1)
        time_stamp = d_package.info_from_hash(all_versions[random_version], arch='amd64')['result'][0]['first_seen']
        COMPLETE_SNAPSHOT_URL = SNAPSHOT_URL.format(time_stamp=time_stamp)
        print "picked version: {v}".format(v=all_versions[random_version])

        os.system('echo normaluse|sudo -S python sources_handler.py {arg}'.format(arg=COMPLETE_SNAPSHOT_URL))
        update()
        pv = VersionParser(self.p)
        # print pv
        # print "CANDIDATES:",[pv.get_candidates()], all_versions[random_version]
        assert (all_versions[random_version] in pv.get_candidates())


if __name__ == '__main__':
    unittest.main()
