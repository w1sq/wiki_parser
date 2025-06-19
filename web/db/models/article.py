from sqlalchemy import (
    Column,
    UUID,
    TEXT,
    INTEGER,
    TIMESTAMP,
    ForeignKey,
    BOOLEAN,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from web.db import DeclarativeBase


class ArticleStorage(DeclarativeBase):
    """Модель для хранения статей Wikipedia"""

    __tablename__ = "articles"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        server_default=func.gen_random_uuid(),
        doc="Unique identifier for the article",
    )
    url = Column(
        TEXT,
        unique=True,
        nullable=False,
        index=True,
        doc="URL of the article",
    )
    title = Column(TEXT, nullable=False, doc="Title of the article")
    content = Column(TEXT, nullable=False, doc="Content of the article")
    status = Column(
        TEXT,
        default="pending",
        doc="Status of the article",
        comment="pending, processing, completed, failed",
    )
    level = Column(
        INTEGER,
        default=0,
        doc="Level of the article",
        comment="Level of the article",
    )
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("articles.id"),
        nullable=True,
        doc="Link to the parent article",
    )
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

    parent = relationship("ArticleStorage", remote_side=[id], backref="children")
    summary = relationship(
        "ArticleSummaryStorage", back_populates="article", uselist=False
    )
    links = relationship("ArticleLinkStorage", back_populates="source_article")


class ArticleSummaryStorage(DeclarativeBase):
    """Модель для хранения summary статей"""

    __tablename__ = "article_summaries"

    id = Column(
        UUID(as_uuid=True),
        server_default=func.gen_random_uuid(),
        primary_key=True,
        unique=True,
        doc="Unique identifier for the summary",
    )
    article_id = Column(
        UUID(as_uuid=True),
        ForeignKey("articles.id"),
        unique=True,
        nullable=False,
        doc="Link to the article",
    )
    text = Column(
        TEXT,
        nullable=False,
        doc="Summary of the article",
        comment="Summary of the article",
    )
    model_used = Column(
        TEXT,
        nullable=False,
        doc="Model used to generate the summary",
        comment="deepseek, chatgpt",
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        doc="Date and time of creation",
    )

    article = relationship("ArticleStorage", back_populates="summary")


class ArticleLinkStorage(DeclarativeBase):
    """Модель для хранения связей между статьями (для рекурсивного парсинга)"""

    __tablename__ = "article_links"

    id = Column(
        UUID(as_uuid=True),
        server_default=func.gen_random_uuid(),
        primary_key=True,
        unique=True,
    )
    source_article_id = Column(
        UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False
    )
    target_url = Column(TEXT, nullable=False, doc="URL of the target article")
    target_title = Column(TEXT, nullable=True, doc="Title of the target article")
    link_text = Column(TEXT, nullable=True, doc="Text of the link")
    is_parsed = Column(BOOLEAN, default=False, doc="Is parsed")
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        doc="Date and time of creation",
    )

    source_article = relationship("ArticleStorage", back_populates="links")
