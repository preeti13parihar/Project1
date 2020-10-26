import os
import time
import json
import boto3
from botocore.client import Config
import botocore
from config import config
from db import db

db = db.Database()

env = config.GetEnvObj()

PBOX_AWS_KEY = env("PBOX_AWS_KEY") if env("PBOX_AWS_KEY") else os.getenv("PBOX_AWS_KEY", None)
PBOX_AWS_SECRET = env("PBOX_AWS_SECRET") if env("PBOX_AWS_SECRET") else os.getenv("PBOX_AWS_SECRET", None)
PBOX_BUCKET = env("PBOX_BUCKET") if env("PBOX_BUCKET") else os.getenv("PBOX_BUCKET", None)
PBOX_REGION = env("PBOX_REGION") if env("PBOX_REGION") else os.getenv("PBOX_REGION", None)
PBOX_S3_URL = env("PBOX_S3_URL") if env("PBOX_S3_URL") else os.getenv("PBOX_S3_URL", None)

# Initialize a session using DigitalOcean Spaces.
session = boto3.session.Session()
client = session.client('s3',
                        region_name=PBOX_REGION,
                        endpoint_url=PBOX_S3_URL,
                        aws_access_key_id=PBOX_AWS_KEY,
                        aws_secret_access_key=PBOX_AWS_SECRET)

s3_obj = boto3.resource('s3')
s3_bucket = s3_obj.Bucket(PBOX_BUCKET)

def list_all_s3_data(username):
    my_bucket = s3_obj.Bucket(PBOX_BUCKET)# + "/" + username + "/")
    for my_bucket_object in my_bucket.objects.all():
        print(my_bucket_object)                          


def s3_get_object(filepath):
    print(filepath)
    file = client.get_object(Bucket=PBOX_BUCKET, Key=filepath)
    return file

def download_file(key, filename):
    # with open('hello.md', 'wb') as data:
    #     s3_bucket.download_fileobj('hello.md', data)    
    #     print(data)
    resp = s3_bucket.download_file(key, filename)
    data = open(filename, mode="rb")
    return data

def list_all_data(user):
    print(PBOX_BUCKET)
    prefix = "/" + PBOX_BUCKET + "/" + user
    response = client.list_objects_v2(Bucket=PBOX_BUCKET) #, Prefix=prefix)
    if 'Contents' in response:
        for item in response['Contents']:
            print(item)
        #   print('deleting file', item['Key'])
        #   client.delete_object(Bucket=PBOX_BUCKET, Key=item['Key'])
        #   while response['KeyCount'] == 1000:
        #     response = client.list_objects_v2(
        #       Bucket=PBOX_BUCKET,
        #       StartAfter=response['Contents'][0]['Key'],
        #     )
        #     for item in response['Contents']:
        #       print('deleting file', item['Key'])
        #       client.delete_object(Bucket=PBOX_BUCKET, Key=item['Key'])


def save_to_s3(data, username, filename, description):
    #In order to generate a file, you must put "/" at the end of key
    # stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    filepath = f"{username}/{filename}"
    print(filepath)
    try:
        start = time.time()
        resp = client.put_object(Bucket=PBOX_BUCKET, Body=data, Key=filepath)
        end = time.time()
        body = {
            "username": username,
            "firstname": username,
            "lastname": username,
            "uploadTime": str(end - start),
            "description": description,
            "filekey": "pbox-storage/" + username + "/" + filename
        }

        db.insert(body)
        

        return resp, True
    except Exception as e:
        print(f"S3 upload error: {str(e)}")
        return str(e), False

# def s3_delete_all_file(folder):
#     bucket = s3.Bucket('aniketbucketpython')
#     d = f"{folder}/"
#     for obj in bucket.objects.filter(Prefix=f):
#         s3.Object(bucket.name,obj.key).delete()

def get_objects_in_folder(folderpath):
    """List all objects in the provided directory.

    1. Set bucket name.
    2. Leave delimiter blank to fetch all files.
    3. Set folder path to "folderpath" parameter.
    4. Return list of objects in folder.
    """
    objects = client.list_objects_v2(
        Bucket='hackers',
        EncodingType='url',
        MaxKeys=1000,
        Prefix=folderpath,
        ContinuationToken='',
        FetchOwner=False,
        StartAfter=''
        )
    return objects


def get_folders():
    """Retrieve all folders within a specified directory.

    1. Set bucket name.
    2. Set delimiter (a character that our target files have in common).
    3. Set folder path to objects using "Prefix" attribute.
    4. Create list of all recursively discovered folder names.
    5. Return list of folders.
    """
    get_folder_objects = client.list_objects_v2(
        Bucket='hackers',
        Delimiter='',
        EncodingType='url',
        MaxKeys=1000,
        Prefix='posts/',
        ContinuationToken='',
        FetchOwner=False,
        StartAfter=''
        )
    folders = [item['Key'] for item in get_folder_objects['Contents']]
    return folders