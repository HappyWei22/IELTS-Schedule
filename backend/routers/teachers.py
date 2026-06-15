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


@router.put("/bulk", response_model=schemas.BulkActionResult)
def update_teachers_bulk(payload: schemas.TeacherBulkUpdate, db: Session = Depends(get_db)):
    if payload.subject is None and payload.note is None:
        raise HTTPException(status_code=400, detail="请至少选择一个要批量修改的字段。")

    teachers = db.query(models.Teacher).filter(models.Teacher.id.in_(payload.ids)).all()
    if len(teachers) != len(set(payload.ids)):
        raise HTTPException(status_code=404, detail="部分老师不存在，请刷新列表后重试。")

    for teacher in teachers:
        if payload.subject is not None:
            teacher.subject = payload.subject
        if payload.note is not None:
            teacher.note = payload.note

    db.commit()
    return schemas.BulkActionResult(affected_count=len(teachers))


@router.post("/bulk-delete", response_model=schemas.BulkActionResult)
def delete_teachers_bulk(payload: schemas.BulkIds, db: Session = Depends(get_db)):
    teachers = db.query(models.Teacher).filter(models.Teacher.id.in_(payload.ids)).all()
    if len(teachers) != len(set(payload.ids)):
        raise HTTPException(status_code=404, detail="部分老师不存在，请刷新列表后重试。")

    blocked = (
        db.query(models.Course.teacher_id)
        .filter(models.Course.teacher_id.in_(payload.ids))
        .distinct()
        .all()
    )
    if blocked:
        blocked_ids = [item[0] for item in blocked]
        blocked_names = [teacher.name for teacher in teachers if teacher.id in blocked_ids]
        raise HTTPException(
            status_code=400,
            detail=f"以下老师已有课程记录，不能批量删除：{'、'.join(blocked_names)}。请先删除相关课程。",
        )

    for teacher in teachers:
        db.delete(teacher)
    db.commit()
    return schemas.BulkActionResult(affected_count=len(teachers))


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
