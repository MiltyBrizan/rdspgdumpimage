import boto3
from botocore.exceptions import ClientError
import os
from os.path import expanduser
import subprocess
import base64
import socket
import datetime

session = boto3.session.Session()


def anon(replace_me):
    length = len(replace_me)

    if length > 5:
        anon_string = "*"*(length-4)+replace_me[-4:]
    else:
        anon_string = '*"*length'

    return anon_string


def show_environment():
    for k, v in os.environ.items():
        print(f'{k}={v}')


def get_aws_keys():
    try:
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    except:
        print ("Something went wront with getting the OS Environment  variables")

    if aws_access_key_id == None:
        print("No AWS Access Key ID provided. Using host credentials if available")
    else:
        print ("AWS ACCESS: {}\nAWS SECRET: {}".format(anon(aws_access_key_id), anon(aws_secret_access_key)))

    return { "AWS_ACCESS_KEY_ID" :  aws_access_key_id ,  "AWS_SECRET_ACCESS_KEY" :  aws_secret_access_key }


def get_secret_string_from_secret_id(secret_id, session, access_key = None, secret_key= None):
    try:
        if access_key:
            print("Attempting boto3 client connection with supplied aws access keys...")
            client = session.client(service_name='secretsmanager', region_name='us-west-2', aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
        else:
            print("Attempting boto3 client connection with instance credentials")
            client = session.client(service_name='secretsmanager', region_name='us-west-2')

        print("[Success] Client connected!\nFetching secret {}.".format(secret_id))    
        getSecretResponse  = client.get_secret_value(SecretId = secret_id)
        print("Success fetching secret {}: ".format(secret_id))
        secret = eval(getSecretResponse['SecretString'])
    except ClientError as e:
        if e.response['Error']['Code'] == "EntityAlreadyExists":
            print("User already exists")
        else:
            print("Unexpected error: %s" % e)

    return secret


def configure_database_from_secret(secret_id, database_name="development", alias="rdsbackup"):
    aws_keys = get_aws_keys()
    database_secret = get_secret_string_from_secret_id( secret_id, session,  access_key=aws_keys["AWS_ACCESS_KEY_ID"], secret_key=aws_keys["AWS_SECRET_ACCESS_KEY"])

    database = {
        "hostname": database_secret['host'],
        "host_ip":  str(socket.gethostbyname(database_secret['host'])),
        "username": database_secret['username'],
        "password": database_secret['password'],
        "port": database_secret['port'],
        "alias": alias,
        "database": database_name,
    }

    return database


def mount_fsx_volume(mount_options, fsx_path, mount_point):
    subprocess.run(["mount", "-t", "cifs", "-o", mount_options, fsx_path, mount_point])


def configure_fsx_from_secret(secret_id):
    aws_keys = get_aws_keys()
    fsx = get_secret_string_from_secret_id( secret_id, session,  access_key=aws_keys["AWS_ACCESS_KEY_ID"], secret_key=aws_keys["AWS_SECRET_ACCESS_KEY"])

    complete_fsx_credentials_path = expanduser("~") +".mountcredentials"
    write_fsx_credentials_to_home(fsx, complete_fsx_credentials_path)
    
    mount_options = "credentials={}".format(complete_fsx_credentials_path)
    mount_point = "/mnt/share/"
    fsx.update({"mount_point" :mount_point })

    mount_fsx_volume(mount_options ,"//{}/{}".format(fsx["ip"], fsx["share"]),  mount_point)
    print("[Success] mounted fsx volume to container!")
    return fsx


def write_fsx_credentials_to_home(fsx, complete_fsx_credentials_path):
    f = open(complete_fsx_credentials_path, "w")
    f.write("user={}\npassword={}\ndomain={}".format(fsx['user'], fsx["password"], fsx["domain"]))
    f.close()


def append_host_file(host_ip, alias):
    # Add the IP Address for the database to the hosts file

    with open("/etc/hosts","a") as f:
        f.write('{}\t{}\n'.format(host_ip, alias))

    print("Wrote out /etc/hosts\n")


def pgdump_to_fsx(target_database, fsx):
    timestamp = datetime.datetime.utcnow().strftime('%B%d%Y%H%M%S')
    pgdump_filename="pgdump_{}.sql".format(timestamp)
    complete_pgdump_path = fsx["mount_point"] + pgdump_filename
    os.environ['PGPASSWORD'] = str(target_database["password"])
    subprocess.run(["pg_dump", "-h", "{}".format(target_database["hostname"]), "-U", "{}".format(target_database["username"]), "--file={}".format(complete_pgdump_path)])


def app_loop():
    database_secret_id = os.getenv("DBSECRET")
    fsx_secret = os.getenv("FSXSECRET")
    database_name = os.getenv("DATABASE_NAME")
    database_alias = os.getenv("DATABASE_ALIAS")

    print("""Entering with the following environmet:
    db_secret_id:      {}
    fsx_secret:           {}
    database_name: {}
    database_aliase:  {}""".format(database_secret_id, fsx_secret, database_name, database_alias))

    target_database = configure_database_from_secret(database_secret_id, database_name=database_name, alias=database_alias)
    fsx = configure_fsx_from_secret(fsx_secret)

    pgdump_to_fsx(target_database, fsx)


app_loop()