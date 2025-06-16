from fastapi import FastAPI
from auth.router import router as auth_router
from guest.router import router as guest_router
from user.router import router as user_router

app = FastAPI()
app.include_router(auth_router, prefix="/api")
app.include_router(guest_router, prefix="/api")
app.include_router(user_router, prefix="/api")


