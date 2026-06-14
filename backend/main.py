from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import Base, engine
from routers import courses, schedules, students, teachers

Base.metadata.create_all(bind=engine)

app = FastAPI(title="IELTS Scheduler API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(students.router)
app.include_router(teachers.router)
app.include_router(courses.router)
app.include_router(schedules.router)


@app.get("/")
def root():
    return {"message": "IELTS Scheduler API is running."}
