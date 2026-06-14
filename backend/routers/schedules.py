from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

import models
import schemas
from database import get_db
from routers.courses import course_to_out

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


def base_schedule_query(db: Session):
    return db.query(models.Course).options(joinedload(models.Course.student), joinedload(models.Course.teacher))


@router.get("/daily", response_model=list[schemas.CourseOut])
def get_daily_schedule(date_filter: date = Query(alias="date"), db: Session = Depends(get_db)):
    courses = (
        base_schedule_query(db)
        .filter(models.Course.course_date == date_filter)
        .order_by(models.Course.start_time.asc(), models.Course.teacher_id.asc())
        .all()
    )
    return [course_to_out(course) for course in courses]


@router.get("/student/{student_id}", response_model=list[schemas.CourseOut])
def get_student_schedule(
    student_id: int,
    start_date: date = Query(),
    end_date: date = Query(),
    db: Session = Depends(get_db),
):
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="结束日期不能早于开始日期。")

    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在。")

    courses = (
        base_schedule_query(db)
        .filter(
            models.Course.student_id == student_id,
            models.Course.course_date >= start_date,
            models.Course.course_date <= end_date,
        )
        .order_by(models.Course.course_date.asc(), models.Course.start_time.asc())
        .all()
    )
    return [course_to_out(course) for course in courses]


@router.get("/teacher/{teacher_id}/monthly", response_model=schemas.TeacherMonthlyScheduleOut)
def get_teacher_monthly_schedule(
    teacher_id: int,
    month: str = Query(pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
):
    teacher = db.get(models.Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="老师不存在。")

    year, month_number = [int(part) for part in month.split("-")]
    start_date = date(year, month_number, 1)
    if month_number == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month_number + 1, 1)

    courses = (
        base_schedule_query(db)
        .filter(
            models.Course.teacher_id == teacher_id,
            models.Course.course_date >= start_date,
            models.Course.course_date < end_date,
        )
        .order_by(models.Course.course_date.asc(), models.Course.start_time.asc())
        .all()
    )

    hours_by_type: dict[str, float] = {}
    for course in courses:
        hours_by_type[course.course_type] = round(
            hours_by_type.get(course.course_type, 0) + course.duration_hours,
            2,
        )

    total_hours = round(sum(course.duration_hours for course in courses), 2)
    return schemas.TeacherMonthlyScheduleOut(
        teacher_id=teacher.id,
        teacher_name=teacher.name,
        month=month,
        total_courses=len(courses),
        total_hours=total_hours,
        type_hours=[
            schemas.CourseTypeHours(course_type=course_type, hours=hours)
            for course_type, hours in sorted(hours_by_type.items())
        ],
        courses=[course_to_out(course) for course in courses],
    )
