from typing import Optional
from datetime import datetime, date, timezone
from sqlalchemy import String, Boolean, DateTime, Date, Text, ForeignKey, Integer, Numeric, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.user import User

class LeaveType(Base):
    __tablename__ = "leave_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    code: Mapped[str] = mapped_column(String(10), unique=True)
    default_days: Mapped[int] = mapped_column(Integer)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requires_document: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint('default_days >= 0', name='check_default_days_positive'),
    )

class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    leave_type_id: Mapped[int] = mapped_column(ForeignKey("leave_types.id", ondelete="CASCADE"))
    year: Mapped[int] = mapped_column(Integer)
    
    total_days: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0)
    used_days: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0)
    available_days: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0)

    user: Mapped["User"] = relationship("User", backref="leave_balances")
    leave_type: Mapped["LeaveType"] = relationship("LeaveType", backref="balances")

    __table_args__ = (
        UniqueConstraint("user_id", "leave_type_id", "year", name="uix_user_leave_year"),
    )

class Leave(Base):
    __tablename__ = "leaves"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    leave_type_id: Mapped[int] = mapped_column(ForeignKey("leave_types.id", ondelete="RESTRICT"))
    
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    total_days: Mapped[float] = mapped_column(Numeric(5, 2))
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    
    document: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    applied_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    secondary_approver_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    approval_level: Mapped[int] = mapped_column(Integer, default=1)
    current_approval_level: Mapped[int] = mapped_column(Integer, default=1)
    requires_multi_level: Mapped[bool] = mapped_column(Boolean, default=False)
    
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    notification_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approval_notification_sent: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], backref="leaves")
    leave_type: Mapped["LeaveType"] = relationship("LeaveType", backref="leaves")
    applied_to: Mapped[Optional["User"]] = relationship("User", foreign_keys=[applied_to_id], backref="leave_requests_received")
    secondary_approver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[secondary_approver_id], backref="secondary_leave_requests")
    approved_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by_id], backref="leaves_approved")
