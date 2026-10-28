import asyncio
import json

from mcp.server.fastmcp import FastMCP

from academy.services import get_course_details, list_courses, list_people


def _as_json(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


async def students_resource() -> str:
    """Read the active student directory as JSON."""
    return _as_json(await asyncio.to_thread(list_people, "student"))


async def teachers_resource() -> str:
    """Read the active teacher directory as JSON."""
    return _as_json(await asyncio.to_thread(list_people, "teacher"))


async def courses_resource() -> str:
    """Read the academy course catalog as JSON."""
    return _as_json(await asyncio.to_thread(list_courses))


async def course_resource(course_code: str) -> str:
    """Read one course and its assignments as JSON."""
    return _as_json(await asyncio.to_thread(get_course_details, course_code))


def register_resources(server: FastMCP) -> None:
    """Register read-only academy resources with an MCP server."""
    server.resource(
        "academy://students",
        name="Student directory",
        description="Active academy students.",
        mime_type="application/json",
    )(students_resource)
    server.resource(
        "academy://teachers",
        name="Teacher directory",
        description="Active academy teachers.",
        mime_type="application/json",
    )(teachers_resource)
    server.resource(
        "academy://courses",
        name="Course catalog",
        description="Academy courses and their teachers.",
        mime_type="application/json",
    )(courses_resource)
    server.resource(
        "academy://courses/{course_code}",
        name="Course details",
        description="Course details and assignments for a course code.",
        mime_type="application/json",
    )(course_resource)
