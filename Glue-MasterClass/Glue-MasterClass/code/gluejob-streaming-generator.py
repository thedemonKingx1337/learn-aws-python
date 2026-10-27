# OURS: adapted from the Udemy course "AWS Glue: The Complete Masterclass".
#
# BLOCKED IN THIS ACCOUNT. The organisation's service control policy denies Kinesis
# in every region checked (ap-southeast-2, us-east-1, us-west-2), so put_record()
# fails with AccessDeniedException. Keep it for reading, not running.
#
# Runs on your own machine, not inside Glue. It reads sample.csv from S3 and sends
# each row to the Kinesis stream "gluejob345" as one JSON record, one row every 0.2
# seconds, to feed the streaming job in gluejob-streaming-transformer.py.
import csv
import json
import boto3
import time
import os

REGION = "ap-southeast-2"  # OURS: the course ran in us-east-1
BUCKET = "bucket101pb"     # OURS: was awsglueudemycourse-datasoup-etl-artifacts
KEY = "etl-artifacts/gluejob-artifacts/gluejob345/configuration/sample.csv"  # OURS: prefix added


def generate(stream_name, kinesis_client):
    s3 = boto3.client('s3', region_name=REGION)
    obj = s3.get_object(Bucket=BUCKET, Key=KEY)
    csvf = obj["Body"].read().decode("utf-8-sig").splitlines()
    csvReader = csv.DictReader(csvf)
    for rows in csvReader:
            #debug info in console
            print(json.dumps(rows))
            time.sleep(0.2)
            kinesis_client.put_record(StreamName=stream_name,
                                      Data=json.dumps(rows),
                                      PartitionKey="partitionkey")
if __name__ == '__main__':
    generate('gluejob345', boto3.client('kinesis', region_name=REGION))
