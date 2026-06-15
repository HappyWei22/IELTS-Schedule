import csv
import io
from datetime import date
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

import models
from database import get_db

router = APIRouter(prefix="/api/export", tags=["exports"])


def base_course_query(db: Session):
    return db.query(models.Course).options(joinedload(models.Course.student), joinedload(models.Course.teacher))


def format_time(value) -> str:
    return value.strftime("%H:%M")


def make_csv_response(filename: str, headers: list[str], rows: list[list[object]]) -> StreamingResponse:
    buffer = io.StringIO()
    buffer.write("\ufeff")
    writer = csv.writer(buffer)
    writer.writerow(headers)
    writer.writerows(rows)
    buffer.seek(0)

    encoded_filename = quote(filename)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
        },
    )


@router.get("/daily")
def export_daily_schedule(date_filter: date = Query(alias="date"), db: Session = Depends(get_db)):
    courses = (
        base_course_query(db)
        .filter(models.Course.course_date == date_filter)
        .order_by(models.Course.start_time.asc(), models.Course.teacher_id.asc())
        .all()
    )

    rows = [
        [
            f"{format_time(course.start_time)}-{format_time(course.end_time)}",
            course.student.name,
            course.teacher.name,
            course.course_type,
            course.duration_hours,
            course.location or "",
            course.note or "",
        ]
        for course in courses
    ]
    total_hours = round(sum(course.duration_hours for course in courses), 2)
    rows.extend(
        [
            [],
            ["统计", "", "", "总时长", total_hours, "", ""],
        ]
    )

    return make_csv_response(
        f"每日总课表-{date_filter}.csv",
        ["上课时间", "学生姓名", "老师姓名", "课程类型", "时长", "线上链接/地点", "备注"],
        rows,
    )


@router.get("/student/{student_id}")
def export_student_schedule(
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
        base_course_query(db)
        .filter(
            models.Course.student_id == student_id,
            models.Course.course_date >= start_date,
            models.Course.course_date <= end_date,
        )
        .order_by(models.Course.course_date.asc(), models.Course.start_time.asc())
        .all()
    )

    rows = [
        [
            course.course_date,
            f"{format_time(course.start_time)}-{format_time(course.end_time)}",
            course.course_type,
            course.teacher.name,
            course.duration_hours,
            course.location or "",
            course.note or "",
        ]
        for course in courses
    ]
    total_hours = round(sum(course.duration_hours for course in courses), 2)
    rows.extend(
        [
            [],
            ["统计", "", "总时长", "", total_hours, "", ""],
        ]
    )

    return make_csv_response(
        f"{student.name}-课表-{start_date}_至_{end_date}.csv",
        ["日期", "上课时间", "课程类型", "老师姓名", "时长", "线上链接/地点", "备注"],
        rows,
    )


@router.get("/teacher/{teacher_id}/monthly")
def export_teacher_monthly_schedule(
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
        base_course_query(db)
        .filter(
            models.Course.teacher_id == teacher_id,
            models.Course.course_date >= start_date,
            models.Course.course_date < end_date,
        )
        .order_by(models.Course.course_date.asc(), models.Course.start_time.asc())
        .all()
    )

    rows = [
        [
            course.course_date,
            format_time(course.start_time),
            format_time(course.end_time),
            course.student.name,
            course.course_type,
            course.duration_hours,
            course.location or "",
            course.note or "",
        ]
        for course in courses
    ]

    total_hours = round(sum(course.duration_hours for course in courses), 2)
    rows.extend(
        [
            [],
            ["统计", "", "", "", "当月总课程数", len(courses), "", ""],
            ["统计", "", "", "", "当月总课时数", total_hours, "", ""],
        ]
    )

    return make_csv_response(
        f"{teacher.name}-{month}-月度课表.csv",
        ["日期", "开始时间", "结束时间", "学生姓名", "课程类型", "时长", "线上链接/地点", "备注"],
        rows,
    )
