from database import async_session_maker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncAttrs
from models import *
from faker import Faker
import random
import asyncio


# Initialize Faker to generate random data
fake = Faker()

def create_user():
    phone_number = fake.phone_number()
    phone_number = phone_number if len(phone_number) < 20 else phone_number[:20]
    return User(
        username=fake.user_name(),
        email=fake.email(),
        phone=phone_number,
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        password_hash=fake.password(),
    )

def create_course(user_id):
    return Course(
        title=fake.bs(),
        description=fake.text(max_nb_chars=500),
        created_by=user_id,
    )

def create_chapter(course_id, user_id):
    return Chapter(
        title=fake.sentence(),
        course_id=course_id,
        created_by=user_id,
    )

def create_lesson(chapter_id, user_id):
    return Lesson(
        title=fake.sentence(),
        description=fake.text(),
        chapter_id=chapter_id,
        created_by=user_id,
    )

def create_quiz(lesson_id, user_id):
    return Quiz(
        title=fake.sentence(),
        description=fake.text(),
        lesson_id=lesson_id,
        created_by=user_id,
    )

def create_quiz_question(quiz_id, user_id):
    return QuizQuestion(
        quiz_id=quiz_id,
        title=fake.sentence(),
        description=fake.text(),
        question_type=random.choice(["multiple_choice", "single_choice", "short_answer"]),
        created_by=user_id,
    )

def create_achievement(user_id):
    return Achievement(
        title=fake.word(),
        description=fake.text(),
        type=random.choice(["course_completion", "quiz_completion", "chapter_completion"]),
    )

# Populate the database with 5 users and related data
async def populate():
    async with async_session_maker() as session:
        for _ in range(5):
            user = create_user()
            session.add(user)
            await session.commit()

            # Create courses for the user
            for _ in range(5):
                course = create_course(user.id)
                session.add(course)
                await session.commit()

                # Create chapters for the course
                for _ in range(5):
                    chapter = create_chapter(course.id, user.id)
                    session.add(chapter)
                    await session.commit()

                    # Create lessons for the chapter
                    for _ in range(5):
                        lesson = create_lesson(chapter.id, user.id)
                        session.add(lesson)
                        await session.commit()

                        # Create quizzes for the lesson
                        for _ in range(5):
                            quiz = create_quiz(lesson.id, user.id)
                            session.add(quiz)
                            await session.commit()

                            # Create quiz questions for the quiz
                            for _ in range(5):
                                quiz_question = create_quiz_question(quiz.id, user.id)
                                session.add(quiz_question)
                                await session.commit()

            # Create achievements for the user
            for _ in range(5):
                achievement = create_achievement(user.id)
                session.add(achievement)
                await session.commit()

asyncio.run(populate())
print("Database populated with 5 entries in each table.")
