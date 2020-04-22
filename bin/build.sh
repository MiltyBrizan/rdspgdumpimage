#! /bin/bash   

docker build -t rdsbackup:`git rev-parse --abbrev-ref HEAD` .