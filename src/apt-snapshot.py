import argparse
from snapshot import SnapshotRequest, get_all_packages

parser = argparse.ArgumentParser(description="find package information in debian.snapshot.org")

# optional
parser.add_argument('-l', '--all-binary-versions', help='find binary package versions and corresponding source names and versions', action='store_true')
parser.add_argument('-ls', '--all-source-versions', help='list all available source versions for this package', action='store_true')
parser.add_argument('-alls', '--all-source-for-package-version', nargs=1, help='list all source files associated with this package at that version')

parser.add_argument('-all-packages', help='all packages', action='store_true')
parser.add_argument("package_name", help="write the binary package name you wish to find", type=str)
args = parser.parse_args()

if args.all_binary_versions:
    package = SnapshotRequest(args.package_name)
    print args.package_name
    print package.find_binary_package_versions_and_corresponding_source_names_and_versions(package)
    package.close()
elif args.all_source_versions:
    package = SnapshotRequest(args.package_name)
    print package.list_all_available_source_versions()
elif args.all_source_for_package_version:
    package = SnapshotRequest(args.package_name)
    # package.list_all_sources_for_this_package_at_version()
    version = getattr(args, 'all_source_for_package_version')[0]
    package.close()
    print package.list_all_sources_for_this_package_at_version(version)
elif args.all_packages == '':
    print get_all_packages()

else:
    print 'OK'
