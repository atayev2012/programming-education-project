from database import Base
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


# Define the User model
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(50), nullable=True)
    email_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)
    profile_picture: Mapped[str] = mapped_column(String(255), nullable=True)
    # User's account status in case of deactivation (ban)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False) 

    # Relationships
    created_chapters = relationship("Chapter", back_populates="created_by_user")
    created_courses = relationship("Course", back_populates="created_by_user")
    created_lessons = relationship("Lesson", back_populates="created_by_user")
    created_quizzes = relationship("Quiz", back_populates="created_by_user")
    created_quiz_questions = relationship("QuizQuestion", back_populates="created_by_user")
    achievements = relationship("UserAchievement", back_populates="user")
    xp = relationship("UserXP", back_populates="user")
    quiz_lives = relationship("UserQuizLife", back_populates="user")
    courses = relationship("UserCourse", back_populates="user")
    chapters = relationship("UserChapter", back_populates="user")
    lessons = relationship("UserLesson", back_populates="user")
    quizzes = relationship("UserQuiz", back_populates="user")
    comments_lesson = relationship("CommentLesson", back_populates="user")
    comments_quiz = relationship("CommentQuiz", back_populates="user")
    notifications = relationship("InAppNotification", back_populates="user")
    support_tickets = relationship("SupportTicket", back_populates="user")
    ticket_ratings = relationship("SupportTicketRating", back_populates="user")


class Chapter(Base):
    __tablename__ = 'chapters'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id'), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    # Relationship to lessons and users
    course = relationship("Course", back_populates="chapters")
    created_by_user = relationship("User", back_populates="created_chapters")
    lessons = relationship("Lesson", back_populates="chapter")
    users = relationship("UserChapter", back_populates="chapter")


class Course(Base):
    __tablename__ = 'courses'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    chapters = relationship("Chapter", back_populates="course")
    created_by_user = relationship("User", back_populates="created_courses")
    users = relationship("UserCourse", back_populates="course")



class Lesson(Base):
    __tablename__ = 'lessons'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(256), nullable=False)
    chapter_id: Mapped[int] = mapped_column(ForeignKey('chapters.id'), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    chapter = relationship("Chapter", back_populates="lessons")
    created_by_user = relationship("User", back_populates="created_lessons")
    materials = relationship("LessonMaterial", back_populates="lesson")
    quizzes = relationship("Quiz", back_populates="lesson")
    comments = relationship("CommentLesson", back_populates="lesson")
    users = relationship("UserLesson", back_populates="lesson")



class LessonMaterial(Base):
    __tablename__ = 'lesson_materials'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey('lessons.id'), nullable=False)
    material_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'video', 'photo', 'text'
    material_content: Mapped[str] = mapped_column(String(5000), nullable=False)  # url or text content
    created_by: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    lesson = relationship("Lesson", back_populates="materials")


class Quiz(Base):
    __tablename__ = 'quizzes'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(256), nullable=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey('lessons.id'), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    lesson = relationship("Lesson", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz")
    created_by_user = relationship("User", back_populates="created_quizzes")
    comments = relationship("CommentQuiz", back_populates="quiz")
    users = relationship("UserQuiz", back_populates="quiz")


class QuizQuestion(Base):
    __tablename__ = 'quiz_questions'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey('quizzes.id'), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(256), nullable=True)
    question_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'multiple_choice', 'single_choice', 'short_answer'
    created_by: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    quiz = relationship("Quiz", back_populates="questions")
    created_by_user = relationship("User", back_populates="created_quiz_questions")
    multiple_choice_options = relationship("QuizQuestionMultipleChoice", back_populates="question")
    single_choice_options = relationship("QuizQuestionSingleChoice", back_populates="question")
    short_answer_options = relationship("QuizQuestionShortAnswer", back_populates="question")


class QuizQuestionMultipleChoice(Base):
    __tablename__ = 'quiz_question_multiple_choice'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(ForeignKey('quiz_questions.id'), nullable=False)
    question_title: Mapped[str] = mapped_column(String(100), nullable=False)
    question_description: Mapped[str] = mapped_column(String(512), nullable=True)


    question = relationship("QuizQuestion", back_populates="multiple_choice_options")
    options = relationship("QuizQuestionMultipleChoiceOption", back_populates="question_multiple_choice")

class QuizQuestionMultipleChoiceOption(Base):
    __tablename__ = 'quiz_question_multiple_choice_options'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    question_multiple_choice_id: Mapped[int] = mapped_column(ForeignKey('quiz_question_multiple_choice.id'), nullable=False)
    choice_text: Mapped[str] = mapped_column(String(256), nullable=False)
    is_correct: Mapped[bool] = mapped_column(default=False, nullable=False)

    question_multiple_choice = relationship("QuizQuestionMultipleChoice", back_populates="options")


class QuizQuestionSingleChoice(Base):
    __tablename__ = 'quiz_question_single_choice'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(ForeignKey('quiz_questions.id'), nullable=False)
    question_title: Mapped[str] = mapped_column(String(100), nullable=False)
    question_description: Mapped[str] = mapped_column(String(512), nullable=True)

    question = relationship("QuizQuestion", back_populates="single_choice_options")
    options = relationship("QuizQuestionSingleChoiceOption", back_populates="question_single_choice")

class QuizQuestionSingleChoiceOption(Base):
    __tablename__ = 'quiz_question_single_choice_options'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    question_single_choice_id: Mapped[int] = mapped_column(ForeignKey('quiz_question_single_choice.id'), nullable=False)
    choice_text: Mapped[str] = mapped_column(String(256), nullable=False)
    is_correct: Mapped[bool] = mapped_column(default=False, nullable=False)

    question_single_choice = relationship("QuizQuestionSingleChoice", back_populates="options")

class QuizQuestionShortAnswer(Base):
    __tablename__ = 'quiz_question_short_answer'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(ForeignKey('quiz_questions.id'), nullable=False)
    question_title: Mapped[str] = mapped_column(String(100), nullable=False)
    question_description: Mapped[str] = mapped_column(String(512), nullable=True)
    correct_answer: Mapped[str] = mapped_column(String(512), nullable=False)

    question = relationship("QuizQuestion", back_populates="short_answer_options")


class UserCourse(Base):
    __tablename__ = 'user_courses'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id'), nullable=False)
    chapter_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Total chapters in the course
    chapter_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Completed chapters
    is_completed: Mapped[bool] = mapped_column(default=False, nullable=False)  # Course completion status
    progress: Mapped[float] = mapped_column(default=0.0, nullable=False)  # Progress in percentage

    user = relationship("User", back_populates="courses")
    course = relationship("Course", back_populates="users")


class UserChapter(Base):
    __tablename__ = 'user_chapters'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    chapter_id: Mapped[int] = mapped_column(ForeignKey('chapters.id'), nullable=False)
    lesson_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Total lessons in the chapter
    lesson_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Completed lessons
    is_completed: Mapped[bool] = mapped_column(default=False, nullable=False)  # Chapter completion status
    progress: Mapped[float] = mapped_column(default=0.0, nullable=False)  # Progress in percentage

    user = relationship("User", back_populates="chapters")
    chapter = relationship("Chapter", back_populates="users")


class UserLesson(Base):
    __tablename__ = 'user_lessons'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    lesson_id: Mapped[int] = mapped_column(ForeignKey('lessons.id'), nullable=False)
    is_completed: Mapped[bool] = mapped_column(default=False, nullable=False)  # Lesson completion status
    progress: Mapped[float] = mapped_column(default=0.0, nullable=False)  # Progress in percentage

    user = relationship("User", back_populates="lessons")
    lesson = relationship("Lesson", back_populates="users")

class UserQuiz(Base):
    __tablename__ = 'user_quizzes'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    quiz_id: Mapped[int] = mapped_column(ForeignKey('quizzes.id'), nullable=False)
    score: Mapped[float] = mapped_column(default=0.0, nullable=False)  # User's score in the quiz
    is_completed: Mapped[bool] = mapped_column(default=False, nullable=False)  # Quiz completion status

    user = relationship("User", back_populates="quizzes")
    quiz = relationship("Quiz", back_populates="users")


class Achievement(Base):
    __tablename__ = 'achievements'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(256), nullable=True)
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)  # URL to the achievement image
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'course_completion', 'quiz_completion', 'chapter_completion', 'lesson_completion'
    qty: Mapped[int] = mapped_column(Integer, nullable=False) # 

    users = relationship("UserAchievement", back_populates="achievement")


class UserAchievement(Base):
    __tablename__ = 'user_achievements'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    achievement_id: Mapped[int] = mapped_column(ForeignKey('achievements.id'), nullable=False)
    date_earned: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="users")

class UserXP(Base):
    __tablename__ = 'user_xp'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Total XP earned by the user
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # User's current level

    user = relationship("User", back_populates="xp")


# User lives that gives user the ability to retry a quiz
class UserQuizLife(Base):
    __tablename__ = 'user_quiz_lives'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    lives: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # Number of lives available for the user

    user = relationship("User", back_populates="quiz_lives")


class CommentLesson(Base):
    __tablename__ = 'comment_lessons'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey('lessons.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    is_approved: Mapped[bool] = mapped_column(default=True, nullable=False)  # Comment approval status

    lesson = relationship("Lesson", back_populates="comments")
    user = relationship("User", back_populates="comments_lesson")

class CommentQuiz(Base):
    __tablename__ = 'comment_quizzes'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey('quizzes.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    is_approved: Mapped[bool] = mapped_column(default=True, nullable=False)  # Comment approval status

    quiz = relationship("Quiz", back_populates="comments")
    user = relationship("User", back_populates="comments_quiz")


class InAppNotification(Base):
    __tablename__ = 'in_app_notifications'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)  # URL to the notification image
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False)  # Notification read status

    user = relationship("User", back_populates="notifications")

class SupportTicket(Base):
    __tablename__ = 'support_tickets'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    subject: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default='open', nullable=False)  # e.g., 'open', 'closed', 'in_progress'
    status_description: Mapped[str] = mapped_column(String(500), nullable=True)  # Additional status information

    user = relationship("User", back_populates="support_tickets")
    ratings = relationship("SupportTicketRating", back_populates="ticket")


class SupportTicketRating(Base):
    __tablename__ = 'support_ticket_ratings'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey('support_tickets.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # Rating value (e.g., 1-5 stars)
    comment: Mapped[str] = mapped_column(String(500), nullable=True)  # Optional comment

    ticket = relationship("SupportTicket", back_populates="ratings")
    user = relationship("User", back_populates="ticket_ratings")