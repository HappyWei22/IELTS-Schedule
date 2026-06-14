from datetime import datetime, timedelta, time

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models


def default_end_time(start_time: time) -> time:
    start_dt = datetime.combine(datetime.today().date(), start_time)
    return (start_dt + timedelta(hours=2)).time().replace(second=0, microsecond=0)


def calculate_duration_hours(start_time: time, end_time: time) -> float:
    start_dt = datetime.combine(datetime.today().date(), start_time)
    end_dt = datetime.combine(datetime.today().date(), end_time)
    if end_dt <= start_dt:
        raise HTTPException(status_code=400, detail="结束时间必须晚于开始时间。")
    return round((end_dt - start_dt).total_seconds() / 3600, 2)


def ensure_student_and_teacher_exist(db: Session, student_id: int, teacher_id: int) -> tuple[models.Student, models.Teacher]:
    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在，请先选择有效学生。")

    teacher = db.get(models.Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="老师不存在，请先选择有效老师。")

    return student, teacher


def find_conflict(
    db: Session,
    *,
    student_id: int,
    teacher_id: int,
    course_date,
    start_time: time,
    end_time: time,
    exclude_course_id: int | None = None,
) -> str | None:
    query = db.query(models.Course).filter(models.Course.course_date == course_date)
    if exclude_course_id:
        query = query.filter(models.Course.id != exclude_course_id)

    courses = query.all()

    for course in courses:
        overlaps = start_time < course.end_time and end_time > course.start_time
        if not overlaps:
            continue

        if course.teacher_id == teacher_id:
            return (
                f"排课冲突：老师{course.teacher.name}在 {course.course_date} "
                f"{course.start_time.strftime('%H:%M')}-{course.end_time.strftime('%H:%M')} "
                f"已经有学生{course.student.name}的{course.course_type}课。"
            )

        if course.student_id == student_id:
            return (
                f"排课冲突：学生{course.student.name}在 {course.course_date} "
                f"{course.start_time.strftime('%H:%M')}-{course.end_time.strftime('%H:%M')} "
                f"已经安排了{course.teacher.name}的{course.course_type}课。"
            )

    return None


def assert_no_conflict(
    db: Session,
    *,
    student_id: int,
    teacher_id: int,
    course_date,
    start_time: time,
    end_time: time,
    exclude_course_id: int | None = None,
) -> None:
    message = find_conflict(
        db,
        student_id=student_id,
        teacher_id=teacher_id,
        course_date=course_date,
        start_time=start_time,
        end_time=end_time,
        exclude_course_id=exclude_course_id,
    )
    if message:
        raise HTTPException(status_code=400, detail=message)
