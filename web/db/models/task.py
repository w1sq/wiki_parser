from sqlalchemy import (
    Column,
    TEXT,
    ForeignKey,
    TIMESTAMP,
    UUID,
    func,
)

from web.db import DeclarativeBase


class TaskStorage(DeclarativeBase):
    """Модель для отслеживания celery-задач"""

    __tablename__ = "tasks"

    id = Column(
        UUID(as_uuid=True),
        server_default=func.gen_random_uuid(),
        primary_key=True,
        unique=True,
    )
    task_id = Column(
        TEXT,
        unique=True,
        nullable=False,
        index=True,
        doc="Unique task identifier",
    )
    task_type = Column(
        TEXT, nullable=False, doc="Type of the task", comment="parse, generate_summary"
    )
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=True)
    status = Column(
        TEXT,
        default="pending",
        doc="Status of the task",
        comment="pending, running, completed, failed",
    )
    result = Column(TEXT, nullable=True, doc="Result of the task")
    error = Column(TEXT, nullable=True, doc="Error of the task")
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        doc="Date and time of creation",
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        doc="Date and time of last update",
    )
