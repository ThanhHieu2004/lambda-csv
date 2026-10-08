import json
from typing import Any

FAILED_MESSAGE = "FAILED"

DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key",
}

def build_response(
        status_code: int,
        data: dict[str, Any],
        headers: dict[str, str] | None = None
) -> dict[str, Any]:
    merged_headers = {**DEFAULT_HEADERS, **(headers or {})}

    return {
        "statusCode": status_code,
        "headers": merged_headers,
        "body": json.dumps(data, ensure_ascii=False)
    }


def success_response(data: dict[str, Any], status_code: int = 200) -> dict[str, Any]:
    return build_response(status_code=status_code, data=data)




def error_response(message: str, status_code: int = 400) -> dict[str, Any]:
    return build_response(status_code=status_code, data={"error": message, "status": FAILED_MESSAGE})
