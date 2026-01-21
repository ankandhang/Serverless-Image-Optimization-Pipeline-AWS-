import boto3
import io
import os
from PIL import Image  # ✅ correct import

print("Pillow loaded:", Image.__version__)

s3 = boto3.client("s3")

OUTPUT_BUCKET = "image-output-ankan"
SIZES = {
    "1080p": (1920, 1080),
    "720p": (1280, 720),
    "480p": (854, 480)
}

def lambda_handler(event, context):
    # Safety check
    if "Records" not in event:
        print("No S3 Records found")
        return {"status": "ignored"}

    for record in event["Records"]:
        input_bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        print(f"Processing {key} from {input_bucket}")

        # Get image from S3
        response = s3.get_object(Bucket=input_bucket, Key=key)
        image_bytes = response["Body"].read()

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        filename = os.path.basename(key)

        for label, size in SIZES.items():
            resized = image.copy()
            resized.thumbnail(size)

            buffer = io.BytesIO()
            resized.save(buffer, format="JPEG", quality=80)
            buffer.seek(0)

            output_key = f"{label}/{filename}"

            s3.put_object(
                Bucket=OUTPUT_BUCKET,
                Key=output_key,
                Body=buffer,
                ContentType="image/jpeg"
            )

            print(f"Saved {output_key}")

    return {"status": "success"}
