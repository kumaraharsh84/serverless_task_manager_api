import os

import boto3
from boto3.dynamodb.conditions import Attr

from common import (
    ALLOWED_STATUS,
    authorize,
    decode_last_key,
    encode_last_key,
    logger,
    parse_limit,
    response,
)

TABLE_NAME = os.environ["TABLE_NAME"]
ddb = boto3.resource("dynamodb")
table = ddb.Table(TABLE_NAME)


def handler(event, context):
    auth_error = authorize(event)
    if auth_error:
        return auth_error

    query = event.get("queryStringParameters") or {}

    limit, limit_error = parse_limit(query)
    if limit_error:
        return limit_error

    last_key, key_error = decode_last_key(query.get("lastKey"))
    if key_error:
        return key_error

    status_filter = query.get("status")
    if status_filter and status_filter not in ALLOWED_STATUS:
        return response(400, {"message": "status must be one of todo, in-progress, done"})

    search_text = (query.get("q") or "").strip()

    filter_expr = Attr("isDeleted").not_exists() | Attr("isDeleted").eq(False)
    if status_filter:
        filter_expr = filter_expr & Attr("status").eq(status_filter)
    if search_text:
        filter_expr = filter_expr & (
            Attr("title").contains(search_text) | Attr("description").contains(search_text)
        )

    scan_args = {
        "FilterExpression": filter_expr,
        "Limit": limit,
    }
    if last_key:
        scan_args["ExclusiveStartKey"] = last_key

    result = table.scan(**scan_args)
    items = result.get("Items", [])
    items.sort(key=lambda x: x.get("createdAt", ""), reverse=True)

    next_key = encode_last_key(result.get("LastEvaluatedKey"))
    logger.info("tasks_listed count=%s status=%s q=%s", len(items), status_filter, search_text)

    return response(
        200,
        {
            "tasks": items,
            "count": len(items),
            "nextKey": next_key,
        },
    )
