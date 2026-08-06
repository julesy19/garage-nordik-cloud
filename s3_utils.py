import boto3
import os

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

BUCKET_NAME = os.getenv("S3_BUCKET")

print("BUCKET_NAME =", BUCKET_NAME)

def upload_file_to_s3(file):

    filename = f"photos/{file.filename}"

    s3.upload_fileobj(
        file,
        BUCKET_NAME,
        filename
    )

    url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"

    return url
   
