from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import SQLAlchemyError
from auth.utils import get_user_by_username
from models import User, Course, UserCourse, UserChapter, UserLesson, UserQuiz, Chapter, Lesson
from sqlalchemy import select
from sqlalchemy.orm import selectinload, load_only, with_loader_criteria
from database import SessionDep
from user.utils import (
    get_course_list_progress, get_my_course_list, get_chapters_progress,
    get_lessons_progress, get_lesson, enroll_to_course
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


@router.get("/lessons/{chapter_id}")
async def lessons(chapter_id: int, session: SessionDep, user: User = Depends(get_user_by_username)):
    lessons = await get_lessons_progress(chapter_id, user, session)
    return {
        "details": {
            "success": True,
            "Message": f"List of lessons for chapter with id:{chapter_id}",
            "data": lessons
        }
    }

@router.get("/lesson/{lesson_id}")
async def lesson(lesson_id: int, session: SessionDep, user: User = Depends(get_user_by_username)):
    lesson = await get_lesson(user, lesson_id, session)
    return {
        "details": {
            "success": True,
            "Message": f"Full data for lesson with id:{lesson_id}",
            "data": lesson
        }
    }


@router.post("/enroll/{course_id}")
async def enroll(course_id: int, session: SessionDep, user: User = Depends(get_user_by_username)):
    user_course = await enroll_to_course(course_id, user, session)

    if not user_course:
        message = f"User has successfully enrolled to course with id:{course_id}"
    else:
        message = f"User already enrolled to course with id:{course_id}"
    return {
            "details":{
                "success": True,
                "messsage": message,
                "data": None,
            }
        }

'''
List of endpoints to prepare
=============================
1. list all courses -> mark subscribed courses === DONE
2. list all my courses with progress ==== DONE
3. load course chapters with progress === DONE
4. load course lessons -> mark completed === DONE
4.5 load lesson with comments(load comments as well) === DONE
5. load course quizzes -> mark completed (load comments as well)
6. load notifications
=========
* load all user info required for entering the main page 
=========

6. enroll to course === DONE
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