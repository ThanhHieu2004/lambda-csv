import boto3
from config import config

s3_client = boto3.client("s3", region_name=config.region)


def generate_upload_url(
        object_key: str, content_type: str = "text/csv"
) -> tuple[str, int]:
    expiry_seconds = config.expiry_seconds
    
    upload_url = s3_client.generate_presigned_url(
        "put_object",
        Params={'Bucket': config.bucket_name, 'Key': object_key, 'ContentType': content_type},
        ExpiresIn=expiry_seconds
    )   

    return upload_url, expiry_seconds
