from datetime import datetime, timezone
from typing import Any
import boto3
from config import config

dynamodb = boto3.resource("dynamodb", region_name=config.region)
job_table = dynamodb.Table(config.job_table_name)

def create_job(job_id: str, object_key: str, filename: str) -> dict[str, Any]:
    now_iso = datetime.now(timezone.utc).isoformat()

    item = {
        "jobId": job_id,
        "status": "UPLOADING",
        "inputKey": object_key,
        "originalFilename": filename,
        "createdAt": now_iso,
        "updatedAt": now_iso,
    }

    job_table.put_item(Item=item)
    return item
