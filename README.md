# Using AWS Batch to back up RDS Postgres Databases

Spin up an AWS Cloud9 environment to use. 
https://console.aws.amazon.com/cloud9

It should ideally be in the same VPC as the RDS and FSX instances.

We're going to use Cloud9 to develop our docker container, push that container 
to the container registry. Once there, we can instruct AWS Batch to use that
image for our batch job which we can trigger whenever we like.

The docker container does 5 things:
- Fetches the database and fsx_volume secrets specified as environment variables
- Writes out a local credential file that will be used for the mount command
- Mounts the FSx volume locally using the specified credentials
- writes out a postgres credential file
- Executes pg_dump, outputting to a file on the FSX Volume (with timestamp)

## Install
```bash
git clone https://github.com/MiltyBrizan/rdspgdumpimage.git
python -m venv .env
source .env/bin/activate
pip3 install -r requirements.txt
```

if we haven't already, we'll need to create the secrets for our image to lookup:

RDS Secret: 

{"username":"*******",
"password":"",
"engine":"postgres",
"host":"******",
"port":5432,
"dbInstanceIdentifier":"backmeup"}"

FSX Secret:
{"username":"*******",
"password":"",
"domain":"******",
"ip":"******",
"share": "*****",
}

We will need to create a role that has access to AWS Secrets Manager so we can assign it to the cloud9 instance (for testing) and the AWS Batch compte environment.

Well also need to create a security group for the cloud9 instance and AWS Batch instances that have access to the fileshare and postgres. After we create the security group, make sure we enable inbound access to postgres and fsx from those 