# MCP Academy

A Django backend for an academy with student and teacher accounts, course
enrollment, assignments, submissions, attendance, a protected REST API, Django
admin, and a local Model Context Protocol (MCP) stdio server.

## Setup

The project expects Python 3.13+ and Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py makemigrations academy
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

Admin interface: <http://127.0.0.1:8000/admin/>  
Health check: <http://127.0.0.1:8000/api/health/>

## API

All academy API endpoints require authentication. Obtain a token by posting
`username` and `password` to `/api/auth/token/`, then send
`Authorization: Token <key>`. New public registrations are always student
accounts; create teacher and administrator accounts using the admin interface.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/api/auth/register/` | Register a student |
| POST | `/api/auth/token/` | Obtain an API token |
| GET/POST | `/api/courses/` | Browse or manage courses |
| GET/POST | `/api/enrollments/` | Browse enrollments or enroll a student |
| GET/POST | `/api/assignments/` | Browse or create assignments |
| GET/POST | `/api/submissions/` | Browse or submit coursework |
| GET/POST | `/api/attendance/` | Browse or record attendance |

Teachers are scoped to their own courses, students can view their own records
and submit work only for active enrollments, and administrators can manage all
records. The Django admin provides the full management interface.

## MCP stdio server

Install the requirements and migrate the database, then configure your MCP host
to launch the server from the project directory:

```json
{
  "mcpServers": {
    "mcp-academy": {
      "command": "C:\\path\\to\\MCPAcademy\\.venv\\Scripts\\python.exe",
      "args": ["-m", "academy.mcp_server"],
      "cwd": "C:\\path\\to\\MCPAcademy"
    }
  }
}
```

MCP tools and resources are separated into `academy/mcp/tools.py` and
`academy/mcp/resources.py`; `academy/mcp_server.py` initializes Django and
starts the stdio transport. Tools can list students and teachers, create
accounts and courses, enroll students, create assignments, and record
attendance. Read-only JSON resources are available at `academy://students`,
`academy://teachers`, `academy://courses`, and `academy://courses/{course_code}`.
MCP stdio tools run as the local OS user that launches the MCP client; use them
only with trusted MCP clients and a trusted local project environment.

To run the MCP process directly, use:

```powershell
.\.venv\Scripts\python.exe -m academy.mcp_server
```

## Configuration

For deployment, set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, and
`DJANGO_ALLOWED_HOSTS` in the environment. The default SQLite database is
intended for local development; configure a production database and HTTPS
before deploying.
