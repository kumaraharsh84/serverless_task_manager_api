import os

import boto3
from botocore.exceptions import ClientError

from common import (
    ALLOWED_PRIORITY,
    ALLOWED_STATUS,
    authorize,
    logger,
    now_iso,
    parse_json_body,
    response,
    validate_due_date,
)

TABLE_NAME = os.environ["TABLE_NAME"]
ddb = boto3.resource("dynamodb")
table = ddb.Table(TABLE_NAME)


def handler(event, context):
    auth_error = authorize(event)
    if auth_error:
        return auth_error

    task_id = (event.get("pathParameters") or {}).get("taskId")
    if not task_id:
        return response(400, {"message": "taskId is required in path"})

    body, parse_error = parse_json_body(event)
    if parse_error:
        return parse_error

    update_parts = ["updatedAt = :updatedAt"]
    expression_values = {":updatedAt": now_iso(), ":false": False}
    expression_names = {}

    if "title" in body:
        title = (body.get("title") or "").strip()
        if not title:
            return response(400, {"message": "title cannot be empty"})
        update_parts.append("title = :title")
        expression_values[":title"] = title

    if "description" in body:
        update_parts.append("description = :description")
        expression_values[":description"] = (body.get("description") or "").strip()

    if "status" in body:
        status = body.get("status")
        if status not in ALLOWED_STATUS:
            return response(400, {"message": "status must be one of todo, in-progress, done"})
        update_parts.append("#status = :status")
        expression_values[":status"] = status
        expression_names["#status"] = "status"

    if "priority" in body:
        priority = body.get("priority")
        if priority not in ALLOWED_PRIORITY:
            return response(400, {"message": "priority must be one of low, medium, high"})
        update_parts.append("priority = :priority")
        expression_values[":priority"] = priority

    if "dueDate" in body:
        due_date = body.get("dueDate")
        if due_date is not None and not validate_due_date(due_date):
            return response(400, {"message": "dueDate must be a valid ISO-8601 datetime"})
        update_parts.append("dueDate = :dueDate")
        expression_values[":dueDate"] = due_date

    if len(update_parts) == 1:
        return response(400, {"message": "No valid fields provided"})

    try:
        update_args = {
            "Key": {"taskId": task_id},
            "UpdateExpression": "SET " + ", ".join(update_parts),
            "ExpressionAttributeValues": expression_values,
            "ConditionExpression": "attribute_exists(taskId) AND (attribute_not_exists(isDeleted) OR isDeleted = :false)",
            "ReturnValues": "ALL_NEW",
        }
        if expression_names:
            update_args["ExpressionAttributeNames"] = expression_names

        result = table.update_item(**update_args)
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        if code == "ConditionalCheckFailedException":
            return response(404, {"message": "Task not found"})
        raise

    logger.info("task_updated taskId=%s", task_id)
    return response(200, {"message": "Task updated", "task": result.get("Attributes", {})})
