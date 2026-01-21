import json
import boto3

s3 = boto3.client("s3")
BUCKET = "image-output-ankan"

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}

    key = params.get("key")
    size = params.get("size")

    if not key or not size:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": "Missing key or size"})
        }

    s3_key = f"{size}/{key}"

    download_url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": BUCKET,
            "Key": s3_key,
            "ResponseContentDisposition": f'attachment; filename="{key}"'
        },
        ExpiresIn=3600
    )

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "download_url": download_url
        })
    }
