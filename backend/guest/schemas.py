from pydantic import BaseModel

class BaseChapter(BaseModel):
    id: int
    title: str
    
    class Config:
        from_attributes = True

class BaseCourse(BaseModel):
    id: int
    title: str
    description: str
    
    class Config:
        from_attributes = True

