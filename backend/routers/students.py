from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/students", tags=["students"])


@router.get("", response_model=list[schemas.StudentOut])
def list_students(keyword: str | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(models.Student).order_by(models.Student.id.desc())
    if keyword:
        query = query.filter(models.Student.name.contains(keyword.strip()))
    return query.all()


@router.post("", response_model=schemas.StudentOut)
def create_student(payload: schemas.StudentCreate, db: Session = Depends(get_db)):
    student = models.Student(**payload.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.put("/{student_id}", response_model=schemas.StudentOut)
def update_student(student_id: int, payload: schemas.StudentUpdate, db: Session = Depends(get_db)):
    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在。")

    for key, value in payload.model_dump().items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在。")

    has_courses = db.query(models.Course).filter(models.Course.student_id == student_id).first()
    if has_courses:
        raise HTTPException(status_code=400, detail="该学生已有课程记录，不能直接删除。请先删除相关课程。")

    db.delete(student)
    db.commit()
    return {"message": "学生已删除。"}
