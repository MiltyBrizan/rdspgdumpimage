#!/bin/bash

aws ecr get-login-password --region us-west-2 | docker login \
    --username AWS \
    --password-stdin AWSACCOUNT.dkr.ecr.us-west-2.amazonaws.com/REPONAME