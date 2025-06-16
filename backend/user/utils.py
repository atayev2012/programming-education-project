from models import User, Course, UserCourse, Chapter, Lesson, CommentLesson, UserLesson, UserQuiz, UserChapter
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import load_only, selectinload, joinedload, with_loader_criteria
from utils import internal_error
from typing import List, Any
from user.schemas import MyCourses, MyChapters, MyLessons, MyLesson
from fastapi import Depends
from database import SessionDep, Base


# load list of all courses
async def get_course_list(session: SessionDep) -> List[Course]:
    statement = select(Course)
    try:
        data = await session.execute(statement)
        courses = data.scalars().all()
        return courses
    except SQLAlchemyError:
        raise internal_error


# load list of courses with enrolled and progress percentage values
async def get_course_list_progress(user: User, session: SessionDep) -> List[MyCourses] | None:
    # get list of courses
    guest_courses_list = await get_course_list(session)
    
    # change format of storage and add progress
    user_courses_list = [MyCourses.model_validate(course) for course in guest_courses_list]

    # load user courses with id, 
    statement = select(UserCourse).filter(UserCourse.user_id == user.id).options(load_only(UserCourse.course_id, UserCourse.progress))
    
    try:
        data = await session.execute(statement)
        enrolled_courses = data.scalars().all()
    except SQLAlchemyError:
        raise internal_error
    
    for enrolled_course in enrolled_courses:
        for i in range(len(user_courses_list)):
            if enrolled_course.course_id == user_courses_list[i].id:
                user_courses_list[i].progress = enrolled_course.progress
                user_courses_list[i].enrolled = True
    return user_courses_list
                

# get data only on my courses
async def get_my_course_list(user: User, session: SessionDep) -> List[MyCourses] | None:
    # load all courses with enrolled and progress values
    courses = await get_course_list_progress(user, session)
    my_courses = []

    # append to result only courses where user was enrolled
    for course in courses:
        if course.enrolled:
            my_courses.append(course)

    return my_courses


# # get any model by id
# async def get_item_by_id(id: int, model: Base, session: SessionDep) -> Any | None:
#     statement = select(model).filter(model.id == id)
#     data = await session.execute(statement)
#     item = data.scalar_one_or_none()
#     return item


# get list of all chapters of a course
async def get_chapters(course_id: int, session: SessionDep) -> MyChapters | None:
    try:
        statement =  select(Course).filter(Course.id == course_id).options(selectinload(Course.chapters))
        data = await session.execute(statement)
        course = data.scalar_one_or_none()

        course.chapters.sort(key=lambda x: x.order if x.order else 1)

        my_cahpters = [MyChapters.model_validate(chapter) for chapter in course.chapters]

        return my_cahpters
    except SQLAlchemyError:
        raise internal_error

# get list of all chapters of a course with progress
async def get_chapters_progress(course_id:int, user: User, session: SessionDep):
    chapters = await get_chapters(course_id, session)

    try:
        statement = select(User).filter(User.id == user.id).options(selectinload(User.chapters))
        data = await session.execute(statement)
        my_chapters = data.scalar_one_or_none().chapters

        for chapter in my_chapters:
            for i in range(len(chapters)):
                if chapter.chapter_id == chapters[i].id:
                    chapters[i].progress = chapter.progress

        return chapters
    except SQLAlchemyError:
        raise internal_error
    

# get list of all lessons of a chapter
async def get_lessons(chapter_id: int, session: SessionDep) -> List[MyLessons]:
    try:
        # load chapter based on id
        statement =  select(Chapter).filter(Chapter.id == chapter_id).options(
    selectinload(Chapter.lessons).options(selectinload(Lesson.quizzes)))
        data = await session.execute(statement)
        chapter = data.scalar_one_or_none()

        # sort all lessons based on order
        chapter.lessons.sort(key=lambda x: x.order if x.order else 1)

        # convert lesson to my lessons
        my_lessons = [MyLessons.model_validate(lesson) for lesson in chapter.lessons]


        return my_lessons
    except SQLAlchemyError as e:
        raise internal_error


# get list of all lessons with progress
async def get_lessons_progress(chapter_id: int, user: User, session: SessionDep):
    # get list of lessons
    lessons = await get_lessons(chapter_id, session)

    lesson_ids = [lesson.id for lesson in lessons]
    quiz_ids = []
    for lesson in lessons:
        quiz_ids.extend(
            [quiz.id for quiz in lesson.quizzes]
        )

    try:
        # get list of lessons user has read
        statement = select(User).filter(User.id == user.id).options(
            selectinload(User.lessons), 
            with_loader_criteria(UserLesson, UserLesson.lesson_id.in_(lesson_ids))).options(
                selectinload(User.quizzes),
                with_loader_criteria(UserQuiz, UserQuiz.quiz_id.in_(quiz_ids))
                )

        data = await session.execute(statement)
        user_data = data.scalar_one_or_none()
    except SQLAlchemyError:
        raise internal_error
    
    user_lessons = user_data.lessons
    user_quizzes = user_data.quizzes

    # update lessons is_read status
    for lesson in user_lessons:
        for i in range(len(lessons)):
            if lesson.lesson_id == lessons[i].id:
                lessons[i].is_read = lesson.is_completed
    
    # update quizzes is_completed and scores
    for quiz in user_quizzes:
        for i in range(len(lessons)):
            for j in range(len(lessons[i].quizzes)):
                if quiz.quiz_id == lessons[i].quizzes[j].id:
                    lessons[i].quizzes[j].is_completed = quiz.is_completed
                    lessons[i].quizzes[j].score = quiz.score

    return lessons

# load lesson with comments
async def get_lesson(user: User, lesson_id: int, session: SessionDep):
    try:
        statement = select(Lesson).filter(Lesson.id == lesson_id).options(
            selectinload(Lesson.materials)).options(
                selectinload(Lesson.comments).options(selectinload(CommentLesson.user))
            )

        data = await session.execute(statement)
        lesson = data.scalar_one_or_none()

        full_lesson = MyLesson.model_validate(lesson)

        # update database, mark lesson as reaad by user
        statement = select(UserLesson).filter(
            UserLesson.user_id == user.id, 
            UserLesson.lesson_id == lesson_id
        )
        data = await session.execute(statement)
        user_lesson = data.scalar_one_or_none()

        if user_lesson:
            if not user_lesson.is_completed:
                user_lesson.is_completed = True
            
            await session.commit()
        else:
            raise internal_error
    except SQLAlchemyError:
        raise internal_error

    return full_lesson


async def enroll_to_course(course_id: int, user:User, session: SessionDep):
    try:
        # check if user already enrolled
        statement = select(User).filter(User.id == user.id).options(
            selectinload(User.courses), with_loader_criteria(UserCourse, UserCourse.course_id == course_id))
        data = await session.execute(statement)
        user_courses = data.scalar_one_or_none().courses

        if not user_courses:
            statement = select(Course).filter(Course.id == course_id).options(
                selectinload(Course.chapters).options(selectinload(Chapter.lessons).options(
                    selectinload(Lesson.quizzes)
                )))
            data = await session.execute(statement)
            course = data.scalar_one_or_none()

            new_course = UserCourse(
                user_id=user.id,
                course_id = course.id,
                chapter_total = len(course.chapters),
                chapter_completed = 0,
                is_completed = False,
                progress = 0
            )

            session.add(new_course)

            for chapter in course.chapters:
                new_chapter = UserChapter(
                    user_id = user.id,
                    chapter_id = chapter.id,
                    lesson_total = len(chapter.lessons),
                    lesson_completed = 0,
                    is_completed = False,
                    progress = 0
                )
                session.add(new_chapter)

                for lesson in chapter.lessons:
                    new_lesson = UserLesson(
                        user_id = user.id,
                        lesson_id = lesson.id,
                        is_completed = False,
                        progress = 0
                    )

                    session.add(lesson)

                    for quiz in lesson.quizzes:
                        new_quiz = UserQuiz(
                            user_id = user.id,
                            quiz_id = quiz.id,
                            score = 0,
                            is_completed = False
                        )

                        session.add(new_quiz)
        
        await session.commit()
    except SQLAlchemyError:
        raise internal_error
    
    return user_courses

