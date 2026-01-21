import json
import boto3
import uuid

s3 = boto3.client("s3")
BUCKET_NAME = "image-input-ankan"

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    filename = params.get("filename")

    if not filename:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": "Missing filename"})
        }

    key = f"{uuid.uuid4()}-{filename}"

    upload_url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": key,
            "ContentType": "image/jpeg"
        },
        ExpiresIn=3600
    )

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,OPTIONS"
        },
        "body": json.dumps({
            "upload_url": upload_url,
            "key": key
        })
    }
