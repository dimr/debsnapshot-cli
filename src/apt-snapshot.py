import argparse
from snapshot import SnapshotRequest, get_all_packages

parser = argparse.ArgumentParser(description="find package information in debian.snapshot.org")

parser.add_argument("package_name", help="write the binary package name you wish to find", type=str)
# optional
parser.add_argument('-l', '--all-binary-versions', help='find binary package versions and corresponding source names and versions', action='store_true')
parser.add_argument('-ls', '--all-source-versions', help='list all available source versions for this package', action='store_true')
parser.add_argument('-alls', '--all-source-for-package-version', type=str, help='list all source files associated with this package at that version')
parser.add_argument('-alb', '--all-binpackages-for-package-version', type=str, help='list all binary packages associated with this source package at that version')
parser.add_argument('-af', '--all-files', type=str, nargs='+', help='list all files associated with this source package at that version')
parser.add_argument('-fs', '--info', type=str, nargs='+', help='get information e.x first_seen')
parser.add_argument('-all-packages', help='all packages', action='store_true')
args = parser.parse_args()

# if args.all_binary_versions:
#     package = SnapshotRequest(args.package_name)
#     print args.package_name
#     print package.find_binary_package_versions_and_corresponding_source_names_and_versions(package)
#     package.close()
the_hash = ''
arch = ''
if args.all_source_versions:
    #python apt-snapshot.py -ls spacefm
    package = SnapshotRequest(args.package_name)
    print package.list_all_available_source_versions()
elif args.all_source_for_package_version:
    #python apt-snapshot.py -alls 0.9.4-2 spacefm
    package = SnapshotRequest(args.package_name)
    # package.list_all_sources_for_this_package_at_version()
    version = getattr(args, 'all_source_for_package_version')
    print package.list_all_sources_for_this_package_at_version(version)
elif args.all_binpackages_for_package_version:
    #python apt-snapshot.py -alb 0.9.4-2 spacefm
    print(args)
    package = SnapshotRequest(args.package_name)
    version = getattr(args, 'all_binpackages_for_package_version')
    print package.list_all_binary_packages_for_this_package_at_version(version)
elif args.all_files:
    #apt-snapshot.py spacefm -af  0.9.4-2 amd64
    print args,"PRLBMEADS"
    package = SnapshotRequest(args.package_name)
    num_parameters = len(getattr(args, 'all_files'))
    version = getattr(args, 'all_files')[0]
    if num_parameters == 1:
        print package.list_all_files_associated_with_this_source_package_at_that_version(version)
        exit()
    arch = getattr(args, 'all_files')[1]
    print package.list_all_files_associated_with_this_source_package_at_that_version(version, arch)
    print getattr(args, 'all_files')[1]
elif args.info:
    #python apt-snapshot.py python-apt --info 0.7.8 amd64
    print args
    package = SnapshotRequest(args.package_name)
    num_parameters = len(getattr(args, 'info'))
    print (getattr(args, 'info'))
    if num_parameters ==1:
        print 'you must set the arch parameter'
        exit()
    version = getattr(args, 'info')[0]
    arch = getattr(args, 'info')[1]
    print package.info_from_hash(version, arch)

else:
    #python apt-snapshot.py -l spacefm
    package = SnapshotRequest(args.package_name)
    print args.package_name
    print package.find_binary_package_versions_and_corresponding_source_names_and_versions(package)
    print 'OK'
