#!/bin/bash

echo "Tagging image with repo tags."
docker tag rdsbackup:latest AWSACCOUNTID.dkr.ecr.us-west-2.amazonaws.com/REPONAME:latest
echo "Pushing image to ecr."
docker push AWSACCOUNTID.dkr.ecr.us-west-2.amazonaws.com/REPONAME:latest