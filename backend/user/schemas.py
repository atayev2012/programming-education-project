from pydantic import BaseModel

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
    order: int
    progress: float = 0.0

    class Config:
        from_attributes = True