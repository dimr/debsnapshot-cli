import os
import sys
from cli import SOURCES_PATH, SNAPSHOT_FILE, SNAPSHOT_URL

argv = sys.argv[1:]
time_stamp = sys.argv[2]
package_name = sys.argv[3]
version = sys.argv[4]

if argv[0] == "append":
    with open(SOURCES_PATH + SNAPSHOT_FILE, 'a') as f:
        f.write("\n###Appended from debsnapshot-cli for {package}:{version}\n".format(package=package_name, version=version))
        f.write(SNAPSHOT_URL.format(time_stamp=time_stamp))
        f.write("\n")
elif argv[0] == "write":
    with open(SOURCES_PATH + SNAPSHOT_FILE, 'w') as f:
        f.write("\n###Appended from debsnapshot-cli for {package}:{version}\n".format(package=package_name, version=version))
        f.write(SNAPSHOT_URL.format(time_stamp=time_stamp))
        f.write("\n")
else:
    raise Exception("Something else is wrong")
