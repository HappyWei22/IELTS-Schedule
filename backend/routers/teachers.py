from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/teachers", tags=["teachers"])


@router.get("", response_model=list[schemas.TeacherOut])
def list_teachers(keyword: str | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(models.Teacher).order_by(models.Teacher.id.desc())
    if keyword:
        query = query.filter(models.Teacher.name.contains(keyword.strip()))
    return query.all()


@router.post("", response_model=schemas.TeacherOut)
def create_teacher(payload: schemas.TeacherCreate, db: Session = Depends(get_db)):
    teacher = models.Teacher(**payload.model_dump())
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


@router.put("/{teacher_id}", response_model=schemas.TeacherOut)
def update_teacher(teacher_id: int, payload: schemas.TeacherUpdate, db: Session = Depends(get_db)):
    teacher = db.get(models.Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="老师不存在。")

    for key, value in payload.model_dump().items():
        setattr(teacher, key, value)

    db.commit()
    db.refresh(teacher)
    return teacher


@router.delete("/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.get(models.Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="老师不存在。")

    has_courses = db.query(models.Course).filter(models.Course.teacher_id == teacher_id).first()
    if has_courses:
        raise HTTPException(status_code=400, detail="该老师已有课程记录，不能直接删除。请先删除相关课程。")

    db.delete(teacher)
    db.commit()
    return {"message": "老师已删除。"}
