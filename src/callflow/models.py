from datetime import datetime
from src.db.database import Base, phone_number
from src.callflow.enums import CallStatus
from sqlalchemy import Integer, func, Text, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Call(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    caller: Mapped[phone_number]
    receiver: Mapped[phone_number]
    started_at: Mapped[datetime]
    status: Mapped[CallStatus] = mapped_column(default=CallStatus.CREATED)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    callrecording: Mapped["CallRecording"] = relationship(
        "CallRecording",
        back_populates="call",
        uselist=False
    )


class CallRecording(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    call_id: Mapped[int] = mapped_column(ForeignKey('calls.id'), unique=True)
    file_path: Mapped[str] = mapped_column(String(500))
    file_name: Mapped[str] = mapped_column(String(255))
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    transcription: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(server_default=func.now())
    call: Mapped["Call"] = relationship(
        "Call",
        back_populates="callrecording",
        uselist=False
    )


