import os
import uuid

import boto3

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

    body, parse_error = parse_json_body(event)
    if parse_error:
        return parse_error

    title = (body.get("title") or "").strip()
    if not title:
        return response(400, {"message": "title is required"})

    status = body.get("status", "todo")
    if status not in ALLOWED_STATUS:
        return response(400, {"message": "status must be one of todo, in-progress, done"})

    priority = body.get("priority", "medium")
    if priority not in ALLOWED_PRIORITY:
        return response(400, {"message": "priority must be one of low, medium, high"})

    due_date = body.get("dueDate")
    if due_date is not None and not validate_due_date(due_date):
        return response(400, {"message": "dueDate must be a valid ISO-8601 datetime"})

    timestamp = now_iso()
    task_id = str(uuid.uuid4())
    item = {
        "taskId": task_id,
        "title": title,
        "description": (body.get("description") or "").strip(),
        "status": status,
        "priority": priority,
        "createdAt": timestamp,
        "updatedAt": timestamp,
        "isDeleted": False,
    }
    if due_date is not None:
        item["dueDate"] = due_date

    table.put_item(Item=item)
    logger.info("task_created taskId=%s", task_id)
    return response(201, {"message": "Task created", "task": item})
