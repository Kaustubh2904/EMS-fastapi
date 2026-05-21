from typing import Optional
from datetime import datetime, date, time, timezone
from sqlalchemy import String, Boolean, DateTime, Date, Time, Text, ForeignKey, Integer, Numeric, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.user import User

class Shift(Base):
    __tablename__ = "shifts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    grace_period_minutes: Mapped[int] = mapped_column(Integer, default=15)
    total_hours: Mapped[float] = mapped_column(Numeric(4, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class Attendance(Base):
    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    date: Mapped[date] = mapped_column(Date, default=datetime.now(timezone.utc).date)
    shift_id: Mapped[Optional[int]] = mapped_column(ForeignKey("shifts.id", ondelete="SET NULL"), nullable=True)
    
    check_in_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    check_in_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    check_in_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    check_in_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    
    check_out_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    check_out_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    check_out_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    check_out_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    
    status: Mapped[str] = mapped_column(String(20), default="absent")
    is_late: Mapped[bool] = mapped_column(Boolean, default=False)
    late_by_minutes: Mapped[int] = mapped_column(Integer, default=0)
    work_hours: Mapped[float] = mapped_column(Numeric(4, 2), default=0.0)
    overtime_hours: Mapped[float] = mapped_column(Numeric(4, 2), default=0.0)
    
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_regularized: Mapped[bool] = mapped_column(Boolean, default=False)
    regularized_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    regularization_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    regularized_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], backref="attendance_records")
    shift: Mapped[Optional["Shift"]] = relationship("Shift", backref="attendances")
    regularized_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[regularized_by_id])

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uix_user_date"),
        Index("idx_user_date", "user_id", "date"),
        Index("idx_date_status", "date", "status"),
    )

class AttendanceRegularization(Base):
    __tablename__ = "attendance_regularizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    attendance_id: Mapped[int] = mapped_column(ForeignKey("attendance.id", ondelete="CASCADE"))
    requested_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    reason: Mapped[str] = mapped_column(Text)
    
    requested_check_in: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    requested_check_out: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    requested_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    status: Mapped[str] = mapped_column(String(20), default="pending")
    approved_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    attendance: Mapped["Attendance"] = relationship("Attendance", backref="regularization_requests")
    requested_by: Mapped["User"] = relationship("User", foreign_keys=[requested_by_id], backref="my_regularization_requests")
    approved_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by_id], backref="approved_regularizations")
