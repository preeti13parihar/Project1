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
session = boto3.Session(aws_access_key_id=PBOX_AWS_KEY, aws_secret_access_key=PBOX_AWS_SECRET)

client = session.client('s3',
                        region_name=PBOX_REGION,
                        endpoint_url=PBOX_S3_URL,
                        aws_access_key_id=PBOX_AWS_KEY,
                        aws_secret_access_key=PBOX_AWS_SECRET)

s3_obj = session.resource('s3')
s3_bucket = s3_obj.Bucket(PBOX_BUCKET)

def list_all_s3_data(username):
    my_bucket = s3_obj.Bucket(PBOX_BUCKET)# + "/" + username + "/")
    for my_bucket_object in my_bucket.objects.all():
        print(my_bucket_object)                          


def get_all_versions(bucket, filename):
    # s3 = boto3.client('s3')
    keys = ["Versions", "DeleteMarkers"]
    results = to_delete = []
    for k in keys:
        try:
            response = client.list_object_versions(Bucket=bucket)[k]
            print(response)
            to_delete = [r["VersionId"] for r in response if r["Key"] == filename]
        except Exception as e:
            print(str(e))

            continue

    results.extend(to_delete)
    return results


def delete_file_s3(key, filename):
    # flag = True
    # for version in get_all_versions(PBOX_BUCKET, filename):
    #     try:
    #         resp = client.delete_object(Bucket=PBOX_BUCKET, Key=filename, VersionId=version)
    #         print(resp)
    #     except Exception as e:
    #         print("Error while deleting from S3:", str(e))
    #         flag = False

    # resp = client.delete_object(
    #     Bucket=PBOX_BUCKET,
    #     Key=key
    # )

    resp = s3_obj.Object(PBOX_BUCKET, key).delete()
    print(resp)
    
    return resp

def download_file(key, filename):
    obj = s3_obj.Object(PBOX_BUCKET, key)
    resp = obj.get()
    print(resp)

    if resp and ("HTTPHeaders" in resp["ResponseMetadata"]):
        headers = {
            "content-disposition": "attachment;filename=" + filename,
            "content-type": resp["ResponseMetadata"]['HTTPHeaders']['content-type'] ,
            "content-length": resp["ResponseMetadata"]['HTTPHeaders']['content-length']
        }

        return resp['Body'].read(), headers

    return None, None
    # with open('hello.md', 'wb') as data:
    #     s3_bucket.download_fileobj('hello.md', data)    
    #     print(data)

    # resp = s3_bucket.download_file(key, filename)
    # data = open(filename, mode="rb")
    # return data

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

