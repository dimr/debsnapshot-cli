#!/usr/bin/env python
import sys, argparse
import os


#
# parser = argparse.ArgumentParser(description="Debian snapshot sources utility program")
# parser.add_argument('package_name',metavar='1')
# parser.add_argument('-p','--package',help='parse the package',required=False)
# parser.add_argument('-b', help='what does bar do', required=False)
# args=vars(parser.parse_args())
#
#
# print args['package_name']
# print 'package_name' in args.keys()


# SOURCES_PATH = '/etc/apt/sources.list.d/'
# print os.path.exists(SOURCES_PATH), os.path.isdir(SOURCES_PATH)
# print os.access(SOURCES_PATH,os.W_OK)
#
# uid = os.geteuid()
# if uid != 0:
# print 'uid is {}'.format(uid)
#     print 'prompt for superuser credentials'
#     os.system('sudo -k')
# if os.path.exists(SOURCES_PATH) and os.path.isdir(SOURCES_PATH):
#     with open(SOURCES_PATH + 'snapshot.list', 'w') as sn_list:
#         sn_list.write('########APPENDED FROM SNAPSHOT HELPER')


#-----------------------------------------------------------------------------------
# print sys.argv
# print os.geteuid()
# snap = ' '.join([i for i in sys.argv[1:]])
# SOURCES_PATH = '/etc/apt/sources.list.d/'
#
# if os.path.exists(SOURCES_PATH) and os.path.isdir(SOURCES_PATH):
#     with open(SOURCES_PATH + 'snapshot.list', 'w') as sn_list:
#         sn_list.write('########APPENDED FROM SNAPSHOT HELPER################\n')
#         sn_list.write(snap + '\n')
#
# os.system('apt-get -o Acquire::Check-Valid-Until=false update')
# os.system('apt-cache policy {package}'.format(package))
#-----------------------------------------------------------------------------------

#
parser = argparse.ArgumentParser(description="find package in debian snapshot")
parser.add_argument("package_name",help="write the package name you wish to find",type=str)
#args = parser.parse_args()

#optional arguments
parser.add_argument("--source","-s",help="get source package",action='store_true')
parser.add_argument('--downgrade','-d',help="Downgrades to the previous version",action="store_true")
parser.add_argument('--target-version','-t',help="Downgrades to the target version specified",action="store_true")
parser.add_argument('--download-deb',help='Downloads deb',action='store_true')
args = parser.parse_args()

if  args.source:
    print 'get SOURCE'
elif args.downgrade:
    print "Downgrading..."
elif args.target_version:
    print "TARGET"
elif args.download_deb:
    print 'Downloading deb'
else:
    print 'you asked for binary package = ',args.package_name

