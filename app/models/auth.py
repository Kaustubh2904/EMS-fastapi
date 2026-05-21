from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.user import User

class Device(Base):
    __tablename__ = "user_devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    device_fingerprint: Mapped[str] = mapped_column(String(64), index=True) # SHA256 hash
    device_name: Mapped[str] = mapped_column(String(255))
    device_type: Mapped[str] = mapped_column(String(50))
    browser: Mapped[str] = mapped_column(String(100), nullable=True)
    browser_version: Mapped[str] = mapped_column(String(50), nullable=True)
    os: Mapped[str] = mapped_column(String(100), nullable=True)
    os_version: Mapped[str] = mapped_column(String(50), nullable=True)
    is_trusted: Mapped[bool] = mapped_column(Boolean, default=False)
    last_used_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    last_ip: Mapped[str] = mapped_column(String(45))
    registered_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship("User", backref="user_devices")

class EmailOTP(Base):
    __tablename__ = "email_otps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    otp_code: Mapped[str] = mapped_column(String(6))
    purpose: Mapped[str] = mapped_column(String(20)) # email_verification, login_2fa, password_reset
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[DateTime] = mapped_column(DateTime)

    user: Mapped["User"] = relationship("User", backref="otps")

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[DateTime] = mapped_column(DateTime)

    user: Mapped["User"] = relationship("User", backref="reset_tokens")

class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("user_devices.id", ondelete="SET NULL"), nullable=True)
    
    session_token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    ip_address: Mapped[str] = mapped_column(String(45))
    location: Mapped[str] = mapped_column(String(200), nullable=True)
    user_agent: Mapped[str] = mapped_column(String, nullable=True)
    
    login_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    last_activity: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    logout_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    is_suspicious: Mapped[bool] = mapped_column(Boolean, default=False)
    flagged_reason: Mapped[str] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship("User", backref="sessions")
    device: Mapped["Device"] = relationship("Device", backref="sessions")
