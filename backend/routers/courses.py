from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

import models
import schemas
from database import get_db
from services.conflicts import (
    assert_no_conflict,
    calculate_duration_hours,
    default_end_time,
    ensure_student_and_teacher_exist,
    find_conflict,
)

router = APIRouter(prefix="/api/courses", tags=["courses"])


def course_to_out(course: models.Course) -> schemas.CourseOut:
    return schemas.CourseOut(
        id=course.id,
        student_id=course.student_id,
        teacher_id=course.teacher_id,
        course_type=course.course_type,
        course_date=course.course_date,
        start_time=course.start_time,
        end_time=course.end_time,
        duration_hours=course.duration_hours,
        note=course.note,
        created_at=course.created_at,
        updated_at=course.updated_at,
        student_name=course.student.name,
        teacher_name=course.teacher.name,
    )


@router.get("", response_model=list[schemas.CourseOut])
def list_courses(
    date_filter: date | None = Query(default=None, alias="date"),
    student_id: int | None = Query(default=None),
    teacher_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(models.Course).options(joinedload(models.Course.student), joinedload(models.Course.teacher))
    if date_filter:
        query = query.filter(models.Course.course_date == date_filter)
    if student_id:
        query = query.filter(models.Course.student_id == student_id)
    if teacher_id:
        query = query.filter(models.Course.teacher_id == teacher_id)

    courses = query.order_by(models.Course.course_date.desc(), models.Course.start_time.asc()).all()
    return [course_to_out(course) for course in courses]


@router.post("/check-conflict", response_model=schemas.ConflictResult)
def check_conflict(payload: schemas.CourseConflictCheck, db: Session = Depends(get_db)):
    end_time = payload.end_time or default_end_time(payload.start_time)
    calculate_duration_hours(payload.start_time, end_time)
    ensure_student_and_teacher_exist(db, payload.student_id, payload.teacher_id)

    message = find_conflict(
        db,
        student_id=payload.student_id,
        teacher_id=payload.teacher_id,
        course_date=payload.course_date,
        start_time=payload.start_time,
        end_time=end_time,
        exclude_course_id=payload.exclude_course_id,
    )
    return schemas.ConflictResult(has_conflict=bool(message), message=message)


@router.post("", response_model=schemas.CourseOut)
def create_course(payload: schemas.CourseCreate, db: Session = Depends(get_db)):
    end_time = payload.end_time or default_end_time(payload.start_time)
    duration_hours = calculate_duration_hours(payload.start_time, end_time)
    ensure_student_and_teacher_exist(db, payload.student_id, payload.teacher_id)
    assert_no_conflict(
        db,
        student_id=payload.student_id,
        teacher_id=payload.teacher_id,
        course_date=payload.course_date,
        start_time=payload.start_time,
        end_time=end_time,
    )

    course = models.Course(
        **payload.model_dump(exclude={"end_time"}),
        end_time=end_time,
        duration_hours=duration_hours,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course_to_out(course)


@router.put("/{course_id}", response_model=schemas.CourseOut)
def update_course(course_id: int, payload: schemas.CourseUpdate, db: Session = Depends(get_db)):
    course = db.get(models.Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在。")

    end_time = payload.end_time or default_end_time(payload.start_time)
    duration_hours = calculate_duration_hours(payload.start_time, end_time)
    ensure_student_and_teacher_exist(db, payload.student_id, payload.teacher_id)
    assert_no_conflict(
        db,
        student_id=payload.student_id,
        teacher_id=payload.teacher_id,
        course_date=payload.course_date,
        start_time=payload.start_time,
        end_time=end_time,
        exclude_course_id=course_id,
    )

    data = payload.model_dump(exclude={"end_time"})
    for key, value in data.items():
        setattr(course, key, value)
    course.end_time = end_time
    course.duration_hours = duration_hours

    db.commit()
    db.refresh(course)
    return course_to_out(course)


@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.get(models.Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在。")

    db.delete(course)
    db.commit()
    return {"message": "课程已删除。"}
