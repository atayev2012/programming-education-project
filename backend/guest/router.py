from fastapi import APIRouter, HTTPException, status
from database import SessionDep
from models import Course, Chapter
from guest.schemas import BaseChapter, BaseCourse
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from utils import internal_error

router = APIRouter(
    prefix="/guest",
    tags=["unauthorized users"]   
)


@router.get("/courses")
async def get_courses(session: SessionDep):
    statement = select(Course)
    try:
        data = await session.execute(statement)
        courses = data.scalars().all()
        
        base_courses = [BaseCourse.model_validate(course) for course in courses]
        return {
            "details": {
                "success": True,
                "message": "List of courses available",
                "data": base_courses
            }
        }
    
    except SQLAlchemyError:
        raise internal_error

@router.get("/chapters/{course_id}")
async def get_course_chapters(course_id: int, session: SessionDep):
    statement = select(Chapter).filter(Chapter.course_id == course_id)

    try:
        data = await session.execute(statement)
        chapters = data.scalars().all()

        base_chapters = [BaseChapter.model_validate(chapter) for chapter in chapters]
        return {
            "details": {
                "success": True,
                "message": f"List of chapters available for course with id:{course_id}",
                "data": base_chapters
            }
        } 
    except SQLAlchemyError:
        raise internal_error