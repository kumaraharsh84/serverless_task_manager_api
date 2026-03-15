import importlib
import json
import os
import pathlib
import sys
import unittest
from unittest.mock import MagicMock, patch

SRC_DIR = pathlib.Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def load_module(module_name: str):
    sys.modules.pop(module_name, None)
    with patch("boto3.resource") as mock_resource:
        table = MagicMock()
        mock_resource.return_value.Table.return_value = table
        module = importlib.import_module(module_name)
    return module, table


class HandlerTests(unittest.TestCase):
    def setUp(self):
        self.previous_table_name = os.environ.get("TABLE_NAME")
        self.previous_api_token = os.environ.get("API_TOKEN")
        os.environ["TABLE_NAME"] = "TasksTable"
        os.environ["API_TOKEN"] = ""

    def tearDown(self):
        if self.previous_table_name is None:
            os.environ.pop("TABLE_NAME", None)
        else:
            os.environ["TABLE_NAME"] = self.previous_table_name

        if self.previous_api_token is None:
            os.environ.pop("API_TOKEN", None)
        else:
            os.environ["API_TOKEN"] = self.previous_api_token

    def test_create_task_returns_201_and_persists_item(self):
        module, table = load_module("create_task")
        event = {
            "body": json.dumps(
                {
                    "title": "Professional polish",
                    "description": "Add CI and tests",
                    "status": "todo",
                    "priority": "high",
                }
            )
        }

        result = module.handler(event, None)
        body = json.loads(result["body"])

        self.assertEqual(result["statusCode"], 201)
        self.assertEqual(body["task"]["title"], "Professional polish")
        table.put_item.assert_called_once()

    def test_list_tasks_applies_filter_and_returns_next_key(self):
        module, table = load_module("list_tasks")
        table.scan.return_value = {
            "Items": [
                {
                    "taskId": "1",
                    "title": "Write tests",
                    "description": "Backend unit tests",
                    "status": "todo",
                    "createdAt": "2026-03-15T10:00:00+00:00",
                    "isDeleted": False,
                }
            ],
            "LastEvaluatedKey": {"taskId": "1"},
        }

        result = module.handler({"queryStringParameters": {"status": "todo", "limit": "5"}}, None)
        body = json.loads(result["body"])

        self.assertEqual(result["statusCode"], 200)
        self.assertEqual(body["count"], 1)
        self.assertIsNotNone(body["nextKey"])
        table.scan.assert_called_once()

    def test_update_task_rejects_invalid_priority(self):
        module, _table = load_module("update_task")
        event = {
            "pathParameters": {"taskId": "abc"},
            "body": json.dumps({"priority": "urgent"}),
        }

        result = module.handler(event, None)
        body = json.loads(result["body"])

        self.assertEqual(result["statusCode"], 400)
        self.assertIn("priority", body["message"])

    def test_delete_task_marks_item_as_deleted(self):
        module, table = load_module("delete_task")
        event = {"pathParameters": {"taskId": "abc"}}

        result = module.handler(event, None)
        body = json.loads(result["body"])

        self.assertEqual(result["statusCode"], 200)
        self.assertEqual(body["taskId"], "abc")
        table.update_item.assert_called_once()


if __name__ == "__main__":
    unittest.main()
