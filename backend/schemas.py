from datetime import date, datetime, time

from pydantic import BaseModel, Field, field_validator


class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str | None = None
    status: str = "在读"
    note: str | None = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(StudentBase):
    pass


class StudentOut(StudentBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TeacherBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    subject: str = Field(..., min_length=1, max_length=100)
    phone: str | None = None
    note: str | None = None


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(TeacherBase):
    pass


class TeacherOut(TeacherBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CourseBase(BaseModel):
    student_id: int
    teacher_id: int
    course_type: str = Field(..., min_length=1, max_length=100)
    course_date: date
    start_time: time
    end_time: time | None = None
    location: str | None = None
    note: str | None = None

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, value):
        return value


class CourseCreate(CourseBase):
    pass


class CourseUpdate(CourseBase):
    pass


class CourseConflictCheck(CourseBase):
    exclude_course_id: int | None = None


class CourseOut(BaseModel):
    id: int
    student_id: int
    teacher_id: int
    course_type: str
    course_date: date
    start_time: time
    end_time: time
    duration_hours: float
    location: str | None
    note: str | None
    created_at: datetime
    updated_at: datetime
    student_name: str
    teacher_name: str

    model_config = {"from_attributes": True}


class ConflictResult(BaseModel):
    has_conflict: bool
    message: str | None = None


class CourseTypeHours(BaseModel):
    course_type: str
    hours: float


class TeacherMonthlyScheduleOut(BaseModel):
    teacher_id: int
    teacher_name: str
    month: str
    total_courses: int
    total_hours: float
    type_hours: list[CourseTypeHours]
    courses: list[CourseOut]
