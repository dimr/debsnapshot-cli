#! /bin/bash

API_URL='http://snapshot.debian.org/mr/binary/'


for i in $(dpkg --get-selections|cut -f1|cut -d":" -f1);
do
curl -s -o /dev/null -w "%{http_code}" $API_URL$i'/';echo '  '$i
done


