# 📋 Serverless Task Manager API

A production-style serverless REST API for managing tasks, built on AWS using Lambda, API Gateway, DynamoDB, and SAM.

---

## 🏗️ Architecture

| Service | Role |
|---|---|
| **AWS Lambda** (Python 3.12) | Business logic & request handling |
| **Amazon API Gateway** | REST API endpoint exposure |
| **Amazon DynamoDB** | NoSQL task persistence |
| **AWS SAM** | Infrastructure as Code & deployment |

---

## ✨ Features

- ✅ Full **CRUD** task operations
- 🔐 Optional **API token authentication** via `x-api-key` header
- 🔍 **Search** across task title and description (`q` param)
- 🏷️ **Filter** tasks by status
- 📄 **Pagination** with `limit` and `lastKey` cursor support
- 🗑️ **Soft delete** — tasks are flagged `isDeleted` rather than permanently removed
- 🕒 **Audit timestamps** — `createdAt`, `updatedAt`, `deletedAt`
- 📊 **Structured CloudWatch logging** for observability

---

## 📌 Task Fields

| Field | Type | Description |
|---|---|---|
| `title` | string | Task title |
| `description` | string | Task details |
| `status` | string | `todo` \| `in-progress` \| `done` |
| `priority` | string | Task priority level |
| `dueDate` | string (ISO 8601) | Due date/time |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/tasks` | Create a new task |
| `GET` | `/tasks` | List tasks (with optional filters) |
| `PUT` | `/tasks/{taskId}` | Update an existing task |
| `DELETE` | `/tasks/{taskId}` | Soft-delete a task |

### Query Parameters for `GET /tasks`

| Parameter | Description | Default |
|---|---|---|
| `status` | Filter by `todo`, `in-progress`, or `done` | — |
| `q` | Search text in title & description | — |
| `limit` | Results per page (1–50) | `10` |
| `lastKey` | Pagination cursor from previous response | — |

---

## 🚀 Getting Started

### Prerequisites

- An [AWS account](https://aws.amazon.com/)
- [AWS CLI](https://aws.amazon.com/cli/) configured (`aws configure`)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) installed
- Python 3.12+

### Installation

```bash
git clone https://github.com/kumaraharsh84/serverless_task_manager_api.git
cd serverless_task_manager_api
pip install -r requirements.txt
```

### Deploy to AWS

```bash
sam build
sam deploy --guided
```

**Guided deploy prompts:**

| Prompt | Suggested Value |
|---|---|
| Stack name | `internship-task-api` |
| Region | `ap-south-1` (or your preferred region) |
| Allow IAM role creation | `Y` |
| Save config | `Y` |
| `ApiToken` parameter | Set a secret value to enable auth, or leave empty to disable |

> 💡 If `ApiToken` is left empty, authentication is disabled. If set, clients must include the same value in the `x-api-key` request header.

---

## 🧪 Testing the API

After deployment, set your API base URL:

```powershell
$api = "https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/v1"
```

Optionally, set your auth header (only required if `ApiToken` was configured):

```powershell
$headers = @{
  "x-api-key"    = "YOUR_TOKEN"
  "Content-Type" = "application/json"
}
```

### Create a Task

```powershell
Invoke-RestMethod -Method POST -Uri "$api/tasks" `
  -ContentType "application/json" `
  -Body '{"title":"Build project","description":"Internship work","status":"todo","priority":"high","dueDate":"2026-03-20T12:00:00+05:30"}'
```

### List Tasks (with filters & pagination)

```powershell
Invoke-RestMethod -Method GET -Uri "$api/tasks?status=todo&q=project&limit=5"
```

### Update a Task

```powershell
Invoke-RestMethod -Method PUT -Uri "$api/tasks/<TASK_ID>" `
  -ContentType "application/json" `
  -Body '{"status":"in-progress","priority":"medium"}'
```

### Delete a Task (soft delete)

```powershell
Invoke-RestMethod -Method DELETE -Uri "$api/tasks/<TASK_ID>"
```

---

## 📁 Project Structure

```
serverless_task_manager_api/
├── src/                  # Lambda function source code
├── events/               # Sample event payloads for local testing
├── template.yaml         # AWS SAM infrastructure definition
├── requirements.txt      # Python dependencies
├── .gitignore
└── README.md
```

---

## 📝 Key Design Decisions

- **Soft delete** preserves data integrity and supports audit trails
- **Opaque pagination tokens** (`lastKey`) abstract DynamoDB's internal cursor, keeping the API clean
- **Optional auth** allows frictionless development/testing while supporting production security
- **SAM template** enables repeatable, version-controlled infrastructure deployments

---

## 🔧 Local Development

You can test Lambda functions locally using SAM:

```bash
sam local invoke -e events/<event-file>.json
sam local start-api
```

---

## 📄 License

This project was developed as part of an AWS internship. Feel free to fork and adapt.