import json
from typing import Any, Dict

from config import config
from utils.logger import setup_logger
from utils.response import build_response, error_response, success_response
from validators import validate_upload_payload

logger = setup_logger(name="api-router", log_level=config.log_level)

def handle_upload_presign(event: Dict[str, Any]) -> Dict[str, Any]:
    raw_body = event.get("body") or "{}"
    try:
        body = json.loads(raw_body)
    except json.JSONDecodeError:
        return error_response(message="Invalid JSON body", status_code=400)

    upload_request, error_message = validate_upload_payload(body)
    if error_message:
        return error_response(message=error_message, status_code=400)

    return success_response(
        {
            "jobId": upload_request.job_id,
            "objectKey": upload_request.s3_key,
            "filename": upload_request.filename,
            "message": "Validation passed."
        },
        status_code=200
    )


def handle_get_job_status(event: Dict[str, Any]) -> Dict[str, Any]:
    query_params = event.get("pathParameters") or {}
    job_id = query_params.get("jobId")

    if not job_id:
        return error_response(message="Missing 'jobId' query parameter", status_code=400)

    return success_response(
        {
            "jobId": job_id,
            "message": "UPLOADING",
            "status": "In Progress"
        },
        status_code=200
    )



def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    http_method = event.get("httpMethod", "").upper()
    resource = event.get("resource", "")

    logger.debug(
        f"Received request: {http_method} {resource}",
        extra={"route": f"{http_method} {resource}"},
    )

    try:
        match (http_method, resource):
            case ("POST", "/uploads/presign"):
                return handle_upload_presign(event)
            
            case ("GET", "/jobs/{jobId}"):
                return handle_get_job_status(event)
            
            case ("OPTIONS", _):
                # Handle CORS preflight requests
                return build_response(status_code=200, data={})

            case _:
                logger.warning(
                    f"Unhandled route: {http_method} {resource}")
                return error_response(
                    message="Route not found", 
                    status_code=404
                )
    except Exception as exc:
        logger.exception(f"Error processing request: {exc}")
        return error_response(
            message="Internal server error", 
            status_code=500
        )
