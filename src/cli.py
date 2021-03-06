from __future__ import print_function
import argparse
from snapshot import SnapshotRequest, get_all_packages
import logging
from utils import logger, check_port
from tabulate import tabulate
import sys
from __init__ import __version__, __title__
import os
from utils import DEFAULT_TIMEOUT, DEBIAN_PORTS
import subprocess

SNAPSHOT_URL = 'deb [check-valid-until=no] http://snapshot.debian.org/archive/debian/{time_stamp} unstable main contrib non-free'
SOURCES_PATH = '/etc/apt/sources.list.d/'
SNAPSHOT_FILE = 'snapshot.list'

# logging.getLogger("requests").setLevel(logging.CRITICAL)
loggerCLI = logging.getLogger(__file__)
# logging.basicConfig(level=logging.DEBUG)
loggerCLI.setLevel(logging.CRITICAL)


def check(time_stamp, package=None, version=None):
    script_name = "snapshot_file_handler.py"
    folder_ok = os.path.exists(SOURCES_PATH) and os.path.isdir(SOURCES_PATH)
    if not folder_ok:
        print("Path does not exists")
    file_ok = os.path.exists(SOURCES_PATH + SNAPSHOT_FILE) and os.path.isfile(SOURCES_PATH + SNAPSHOT_FILE)
    # root=0 non_root=1000
    normal_user = True if os.geteuid() is not 0 else False
    if file_ok and normal_user:
        subprocess.call(['sudo','-k','python',os.path.join(os.path.dirname(__file__), script_name),'append',time_stamp,package,version])
    elif not file_ok and normal_user:
        subprocess.call(['sudo','-k','python',os.path.join(os.path.dirname(__file__), script_name),'write',time_stamp,package,version])
    elif not normal_user:
        print("you should not run this script as sudo user")


def create_parser(args=None):
    parser = argparse.ArgumentParser(description="find package information in debian.snapshot.org")

    # parser.add_argument('architecture', nargs='?', type=str, default=None, help='set the target version of the package you wish you')
    parser.add_argument("package_version", nargs=argparse.OPTIONAL, default=None, help='set the target version of the package you wish you')
    parser.add_argument("package_name", help="write the package name you wish to find", type=str, default=None)
    # optional
    parser.add_argument('-lb', '--all-binary-versions', help='find binary package versions and corresponding source names and versions', action='store_true')
    parser.add_argument('-ls', '--all-source-versions', help='list all available source versions for this package', action='store_true')
    # parser.add_argument('-alsfpv', '--all-source-for-package-version', help='list all source files associated with this package at that version', action='store_true')
    parser.add_argument('-lbins', '--all-binpackages-for-package-version', help='list all binary packages associated with this source package at that version', action='store_true')
    # parser.add_argument('-af', '--all-files', help='list all files associated with this source package at that version', action='store_true')
    parser.add_argument('--first-seen', help='get information e.x first_seen', action='store_true')
    parser.add_argument('-arch', '--architecture', nargs=1, type=str, choices=DEBIAN_PORTS, help='define system architecture')
    parser.add_argument('--time-out', nargs=1, default=DEFAULT_TIMEOUT, help='set timeout')
    # parser.add_argument('-all-packages', help='all packages', action='store_true')
    parser.add_argument('-v', '--version', help='print debsnapshot-cli version', action='version', version=' : '.join((__title__, __version__)))
    parser.add_argument('-w', '--write-to-file', help="add url entry to /etc/apt/sources.list.d/snapshot.list", action="store_true")
    # parser.parse_args('--proxy fawef fds grea'.split())
    # args = parser.parse_args(args)
    return parser.parse_args(args)


def main(args=None):
    args = create_parser(args)
    timeout = args.time_out
    if timeout == DEFAULT_TIMEOUT:
        package = SnapshotRequest(args.package_name)
    else:
        package = SnapshotRequest(args.package_name, timeout=float(args.time_out[0]))

    if args.package_version is None:
        if args.all_source_versions:
            loggerCLI.debug(args)
            # pprint.pprint(package.list_all_available_source_versions())
            result = package.list_all_available_source_versions()
            print(tabulate([[i] for i in result], tablefmt='grid', headers=["version"]))
            print('\nNumber of versions: ', len(result))
            # else:
            #     package = SnapshotRequest(args.package_name)
            #     result = package.list_all_sources_for_this_package_at_version(args.version[0])
            #     print(tabulate(result['result'], tablefmt='grid', headers='keys'))
        elif args.all_binary_versions:
            package = SnapshotRequest(args.package_name)
            result = package.find_binary_package_versions_and_corresponding_source_names_and_versions(package)
            print(tabulate(result['result'], tablefmt='grid', headers='keys'))  # , tablefmt='simple'))
            print('\nNumber of packages: %d' % len(result['result']))
        else:
            loggerCLI.debug(args)
            # package = SnapshotRequest(args.package_name, timeout=timeout)
            result = package.general_info()
            print(tabulate(result, tablefmt='grid', headers='keys'))  # , tablefmt='simple'))

    elif args.package_version is not None:
        if args.all_source_versions:
            result = package.list_all_sources_for_this_package_at_version(args.package_version)
            print(tabulate(result['result'], tablefmt='grid', headers='keys'))
        elif args.all_binpackages_for_package_version:
            result = package.list_all_binary_packages_for_this_package_at_version(args.package_version)
            print(tabulate(result, tablefmt='grid', headers='keys'))
        elif args.first_seen and args.architecture:
            loggerCLI.debug(args)
            package = SnapshotRequest(args.package_name)
            result = package.info_from_hash(args.package_version, check_port(args.architecture[0]))
            result['result'][0].setdefault('hash', result['hash'])
            print('\n')
            print(tabulate(result['result'], headers='keys'))
            print('\n')
            time_stamp = result['result'][0]['first_seen']
            url = SNAPSHOT_URL.format(time_stamp=time_stamp)
            result = {'URL': url}
            print(tabulate([result], headers="keys"))
            if not args.write_to_file:
                sys.exit()
            # print('URL: ' + SNAPSHOT_URL.format(time_stamp=time_stamp))
            else:
                print('\n')
                print("Append this URL to /etc/apt/sources.list.d/snapshot.list?")
                proceed = raw_input("do you want to continue [y/n/Y/N]:")
                ans = lambda x: x.strip().lower()
                if ans(proceed) == 'y':
                    print("Please enter your sudo password:")
                    check(time_stamp, package=args.package_name, version=args.package_version)
                elif ans == 'n':
                    print('\nBye!')
                    sys.exit()


if __name__ == '__main__':
    main(sys.argv[1:])
