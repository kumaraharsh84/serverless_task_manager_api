import os

import boto3
from botocore.exceptions import ClientError

from common import authorize, logger, now_iso, response

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

    timestamp = now_iso()

    try:
        table.update_item(
            Key={"taskId": task_id},
            UpdateExpression="SET isDeleted = :true, deletedAt = :deletedAt, updatedAt = :updatedAt",
            ExpressionAttributeValues={
                ":true": True,
                ":false": False,
                ":deletedAt": timestamp,
                ":updatedAt": timestamp,
            },
            ConditionExpression="attribute_exists(taskId) AND (attribute_not_exists(isDeleted) OR isDeleted = :false)",
        )
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        if code == "ConditionalCheckFailedException":
            return response(404, {"message": "Task not found"})
        raise

    logger.info("task_soft_deleted taskId=%s", task_id)
    return response(200, {"message": "Task deleted", "taskId": task_id})
