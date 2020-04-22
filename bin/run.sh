#!/bin/bash

docker run \
--privileged \
-it \
-e DBSECRET="prod/backmeup"  \
-e FSXSECRET="prod/fsx_volume"  \
-e DATABASE_NAME="backmeup"  \
-e DATABASE_ALIAS="rdsbackup"  \
-e AWS_ACCESS_KEY_ID=""  \
-e AWS_SECRET_ACCESS_KEY=""  \
rdsbackup:`git rev-parse --abbrev-ref HEAD`