from pydantic import BaseModel
from typing import List
from datetime import datetime

class MyCourses(BaseModel):
    id: int
    title: str
    description: str
    progress: float = 0.0
    enrolled: bool = False

    class Config:
        from_attributes = True


class MyChapters(BaseModel):
    id: int
    title: str
    order: int | None
    progress: float = 0.0

    class Config:
        from_attributes = True


class MyLessonMaterials(BaseModel):
    material_type: str
    material_content: str
    order: int | None

    class Config:
        from_attributes = True


class MyQuizzes(BaseModel):
    id: int
    title: str
    description: str
    is_completed: bool = False
    score: float = 0

    class Config:
        from_attributes = True


class CommentUser(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    profile_picture: str | None

    class Config:
        from_attributes = True


class Comment(BaseModel):
    id: int
    content: str
    is_approved: bool = True
    user: CommentUser
    created_at: datetime

    class Config:
        from_attributes = True


class MyLessons(BaseModel):
    id: int
    title: str
    order: int | None
    description: str
    is_read: bool = False
    quizzes: List[MyQuizzes]

    class Config:
        from_attributes = True


class MyLesson(BaseModel):
    id: int
    title: str
    description: str
    materials: List[MyLessonMaterials]
    comments: List[Comment]

    
    class Config:
        from_attributes = True