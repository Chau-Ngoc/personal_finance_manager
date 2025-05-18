import email.parser
import email.policy
import json

import boto3

mail_parser = email.parser.BytesParser(policy=email.policy.default)

with open("object.json", "r") as f:
    data = json.load(f)

bucket_name = data["Records"][0]["s3"]["bucket"]["name"]
bucket_keyname = data["Records"][0]["s3"]["object"]["key"]

s3 = boto3.client("s3")
response = s3.get_object(Bucket=bucket_name, Key=bucket_keyname)
byte_content = response["Body"].read()

mess = mail_parser.parsebytes(byte_content)
print(mess.as_string())

for part in mess.walk():
    print(part.get_content_type())
    if part.get_content_type() == "text/html":
        print(part.get_content())
