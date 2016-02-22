from __future__ import print_function
import argparse
from snapshot import SnapshotRequest, get_all_packages
import pprint
from utils import logger, check_port
from tabulate import tabulate
import sys


def main(args=None, stdin=None):
    if stdin is None:
        stdin = sys.stdin

    parser = argparse.ArgumentParser(description="find package information in debian.snapshot.org")

    # parser.add_argument('architecture', nargs='?', type=str, default=None, help='set the target version of the package you wish you')
    parser.add_argument("package_name", help="write the package name you wish to find", type=str)
    parser.add_argument('-v', '--version', nargs=1, type=str, help='set the target version of the package you wish you')
    # optional
    parser.add_argument('-lb', '--all-binary-versions', help='find binary package versions and corresponding source names and versions', action='store_true')
    parser.add_argument('-ls', '--all-source-versions', help='list all available source versions for this package', action='store_true')
    # parser.add_argument('-alsfpv', '--all-source-for-package-version', help='list all source files associated with this package at that version', action='store_true')
    parser.add_argument('-lbins', '--all-binpackages-for-package-version', help='list all binary packages associated with this source package at that version', action='store_true')
    # parser.add_argument('-af', '--all-files', help='list all files associated with this source package at that version', action='store_true')
    parser.add_argument('-i', '--info', help='get information e.x first_seen', action='store_true')
    parser.add_argument('-arch', '--architecture', nargs=1, type=str, help='define system architecture')
    # parser.add_argument('-all-packages', help='all packages', action='store_true')
    args = parser.parse_args(args)

    if args.all_source_versions:
        if not args.version:
            package = SnapshotRequest(args.package_name)
            # pprint.pprint(package.list_all_available_source_versions())
            result = package.list_all_available_source_versions()
            print(tabulate([[i] for i in result], tablefmt='grid', headers=["version"]))
            print('\nNumber of versions: ', len(result))
        else:
            package = SnapshotRequest(args.package_name)
            result = package.list_all_sources_for_this_package_at_version(args.version[0])
            print(tabulate(result['result'], tablefmt='grid', headers='keys'))
    elif args.all_binary_versions:
        package = SnapshotRequest(args.package_name)
        result = package.find_binary_package_versions_and_corresponding_source_names_and_versions(package)
        print(tabulate(result['result'], tablefmt='grid', headers='keys'))  # , tablefmt='simple'))
        print('\nNumber of packages: %d' % len(result['result']))
    elif args.all_binpackages_for_package_version:
        package = SnapshotRequest(args.package_name)
        result = package.list_all_binary_packages_for_this_package_at_version(args.version[0])
        print(tabulate(result, tablefmt='grid', headers='keys'))
        # NOT IMPLEMENTED FOR NOW
    # elif args.all_files:
    #     package = SnapshotRequest(args.package_name)
    #     print(args)
    #     print('---------------------------')
    #     # num_parameters = len(getattr(args, 'all_files'))
    #     # version = getattr(args, 'all_files')[0]
    #     if args.architecture is None:
    #         pprint.pprint(package.list_all_files_associated_with_this_source_package_at_that_version(args.version[0]))
    #         exit()
    #     # arch = getattr(args, 'all_files')[1]
    #     architecture = check_port(args.architecture[0])
    #     # pprint.pprint(package.list_all_files_associated_with_this_source_package_at_that_version(args.version[0], architecture), width=1)
    #     result = package.list_all_files_associated_with_this_source_package_at_that_version(args.version[0], architecture)
    #     print(tabulate(result['binaries'][0]['files'], tablefmt='grid', headers='keys'))
    #     # print getattr(args, 'all_files')[1]
    elif args.info:
        package = SnapshotRequest(args.package_name)
        result = package.info_from_hash(args.version[0], args.architecture[0])
        result['result'][0].setdefault('hash', result['hash'])
        print('\n')
        print(tabulate(result['result'], headers='keys'))
        print('\n')
    else:
        package = SnapshotRequest(args.package_name)
        print(args.package_name)
        result = package.general_info()
        print(tabulate(result, tablefmt='grid', headers='keys'))  # , tablefmt='simple'))

    return args


if __name__ == '__main__':
    main(sys.argv[1:])
