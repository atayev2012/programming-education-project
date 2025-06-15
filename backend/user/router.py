from fastapi import APIRouter, Depends
from auth.utils import get_user_by_username
from models import User, Course, UserCourse
from sqlalchemy import select
from sqlalchemy.orm import selectinload, load_only
from database import SessionDep
from user.utils import (
    get_course_list_progress, get_my_course_list, get_chapters_progress
    )

router = APIRouter(
    prefix="/user",
    tags=["users"]
)


@router.get("/courses")
async def courses(session: SessionDep, user = Depends(get_user_by_username)):
    courses = await get_course_list_progress(user, session)
    return {
        "details":{
            "success": True,
            "message": "The list of courses",
            "data": courses
        }
    }

@router.get("/my_courses")
async def my_courses(session: SessionDep, user = Depends(get_user_by_username)):
    my_courses = await get_my_course_list(user, session)
    return {
        "details":{
            "success": True,
            "message": "The list of courses",
            "data": my_courses
        }
    }


@router.get("/chapters/{course_id}")
async def chapters(course_id: int, session: SessionDep, user = Depends(get_user_by_username)):
    chapters = await get_chapters_progress(course_id, user, session)

    return {
        "details": {
            "success": True,
            "message": f"The list of chapters for course with id:{course_id}",
            "data": chapters
        }
    }


@router.get("chapter/lessons/{chapter_id}")
async def lessons(chapter_id: int, session: SessionDep, user: User = Depends(get_user_by_username)):
    pass

'''
List of endpoints to prepare
=============================
1. list all courses -> mark subscribed courses === DONE
2. list all my courses with progress ==== DONE
3. load course chapters with progress === DONE
4. load course lessons -> mark completed (load comments as well)
5. load course quizzes -> mark completed (load comments as well)
6. load notifications
=========
* load all user info required for entering the main page 
=========

6. read lesson -> update progress in database
7. solve quiz -> update progress in database
8. send comment to lesson or quiz
9. send ticket
10. rate ticket
10. mark if notifications read

11. profile -> change info (bio, email, password, image)






enroll to course -> (POST) api/user/enroll
update progress lesson read -> api/user/lesson
update progress quiz solved -> 


'''