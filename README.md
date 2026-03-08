# AWS Internship Project: Serverless Task Manager API

This backend project uses:
- AWS Lambda (Python)
- Amazon API Gateway (REST API)
- Amazon DynamoDB (NoSQL)
- AWS SAM (Infrastructure as Code + deployment)

## Features
- CRUD task APIs
- Optional API token authentication (`x-api-key` header)
- Task fields: `title`, `description`, `status`, `priority`, `dueDate`
- Filters: `status`
- Search: `q` (search in title + description)
- Pagination: `limit` and `lastKey`
- Soft delete (`isDeleted`) instead of hard delete
- Audit timestamps: `createdAt`, `updatedAt`, `deletedAt`
- Structured Lambda logging for CloudWatch

## Endpoints
- `POST /tasks`
- `GET /tasks`
- `PUT /tasks/{taskId}`
- `DELETE /tasks/{taskId}`

## Query Params for GET /tasks
- `status`: `todo | in-progress | done`
- `q`: search text
- `limit`: `1-50` (default `10`)
- `lastKey`: opaque pagination token returned by previous response

## Prerequisites
- AWS account
- AWS CLI configured (`aws configure`)
- AWS SAM CLI installed
- Python 3.12+

## Deploy
```bash
sam build
sam deploy --guided
```

During guided deploy:
- Stack name: `internship-task-api`
- Region: for example `ap-south-1`
- Allow IAM role creation: `Y`
- Save config: `Y`
- Optional parameter `ApiToken`: set a secret value if you want auth enabled

If `ApiToken` is empty, auth is disabled.
If set, pass the same value in `x-api-key` header.

## Test
Set API base URL:
```powershell
$api="https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/v1"
```

Optional auth header (only if ApiToken was set):
```powershell
$headers=@{"x-api-key"="YOUR_TOKEN";"Content-Type"="application/json"}
```

Create:
```powershell
Invoke-RestMethod -Method POST -Uri "$api/tasks" -ContentType "application/json" -Body '{"title":"Build project","description":"Internship work","status":"todo","priority":"high","dueDate":"2026-03-20T12:00:00+05:30"}'
```

List with filters and pagination:
```powershell
Invoke-RestMethod -Method GET -Uri "$api/tasks?status=todo&q=project&limit=5"
```

Update:
```powershell
Invoke-RestMethod -Method PUT -Uri "$api/tasks/<TASK_ID>" -ContentType "application/json" -Body '{"status":"in-progress","priority":"medium"}'
```

Delete (soft delete):
```powershell
Invoke-RestMethod -Method DELETE -Uri "$api/tasks/<TASK_ID>"
```

## Internship Talking Points
- Built a production-style serverless API on AWS.
- Implemented validation, auth option, audit fields, and soft delete.
- Added API filtering/search/pagination for scalable task retrieval.
- Deployed repeatably with SAM template-driven infrastructure.
