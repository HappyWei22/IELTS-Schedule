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


@router.put("/bulk", response_model=schemas.BulkActionResult)
def update_students_bulk(payload: schemas.StudentBulkUpdate, db: Session = Depends(get_db)):
    if payload.status is None and payload.note is None:
        raise HTTPException(status_code=400, detail="请至少选择一个要批量修改的字段。")

    students = db.query(models.Student).filter(models.Student.id.in_(payload.ids)).all()
    if len(students) != len(set(payload.ids)):
        raise HTTPException(status_code=404, detail="部分学生不存在，请刷新列表后重试。")

    if payload.status is not None and payload.status not in ["在读", "暂停", "结课"]:
        raise HTTPException(status_code=400, detail="学生状态只能是：在读、暂停、结课。")

    for student in students:
        if payload.status is not None:
            student.status = payload.status
        if payload.note is not None:
            student.note = payload.note

    db.commit()
    return schemas.BulkActionResult(affected_count=len(students))


@router.post("/bulk-delete", response_model=schemas.BulkActionResult)
def delete_students_bulk(payload: schemas.BulkIds, db: Session = Depends(get_db)):
    students = db.query(models.Student).filter(models.Student.id.in_(payload.ids)).all()
    if len(students) != len(set(payload.ids)):
        raise HTTPException(status_code=404, detail="部分学生不存在，请刷新列表后重试。")

    blocked = (
        db.query(models.Course.student_id)
        .filter(models.Course.student_id.in_(payload.ids))
        .distinct()
        .all()
    )
    if blocked:
        blocked_ids = [item[0] for item in blocked]
        blocked_names = [student.name for student in students if student.id in blocked_ids]
        raise HTTPException(
            status_code=400,
            detail=f"以下学生已有课程记录，不能批量删除：{'、'.join(blocked_names)}。请先删除相关课程。",
        )

    for student in students:
        db.delete(student)
    db.commit()
    return schemas.BulkActionResult(affected_count=len(students))


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
