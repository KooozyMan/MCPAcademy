import asyncio
import os
from datetime import date, datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from mcp.server.fastmcp import FastMCP

from .services import (
    create_assignment,
    create_course,
    create_student,
    create_teacher,
    enroll_student,
    list_courses,
    list_people,
    record_attendance,
)

mcp = FastMCP("MCP Academy")


@mcp.tool()
async def list_students() -> list[dict]:
    """List active student accounts."""
    return await asyncio.to_thread(list_people, "student")


@mcp.tool()
async def list_teachers() -> list[dict]:
    """List active teacher accounts."""
    return await asyncio.to_thread(list_people, "teacher")


@mcp.tool()
async def create_student_account(
    username: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
    email: str = "",
) -> dict:
    """Create a student account."""
    user = await asyncio.to_thread(
        create_student, username, password, first_name, last_name, email
    )
    return {"id": user.pk, "username": user.username, "role": user.role}


@mcp.tool()
async def create_teacher_account(
    username: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
    email: str = "",
) -> dict:
    """Create a teacher account."""
    user = await asyncio.to_thread(
        create_teacher, username, password, first_name, last_name, email
    )
    return {"id": user.pk, "username": user.username, "role": user.role}


@mcp.tool()
async def list_courses_tool() -> list[dict]:
    """List courses and their teachers."""
    return await asyncio.to_thread(list_courses)


@mcp.tool()
async def create_course_tool(title: str, code: str, teacher_username: str, description: str = "") -> dict:
    """Create a course assigned to an existing teacher."""
    return await asyncio.to_thread(create_course, title, code, teacher_username, description)


@mcp.tool()
async def enroll_student_tool(student_username: str, course_code: str) -> dict:
    """Enroll a student in an active course."""
    return await asyncio.to_thread(enroll_student, student_username, course_code)


@mcp.tool()
async def create_assignment_tool(
    course_code: str,
    title: str,
    due_at: str,
    description: str = "",
    points: int = 100,
) -> dict:
    """Create an assignment. due_at must be an ISO 8601 datetime."""
    return await asyncio.to_thread(
        create_assignment,
        course_code,
        title,
        datetime.fromisoformat(due_at),
        description,
        points,
    )


@mcp.tool()
async def record_attendance_tool(
    course_code: str,
    student_username: str,
    attendance_date: str,
    status: str,
    note: str = "",
) -> dict:
    """Record present, absent, late, or excused attendance for an enrolled student."""
    return await asyncio.to_thread(
        record_attendance,
        course_code,
        student_username,
        date.fromisoformat(attendance_date),
        status,
        note,
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
