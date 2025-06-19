from datetime import datetime

from pydantic import BaseModel, Field


class SummaryResponse(BaseModel):
    """Схема для ответа с summary статьи"""

    url: str = Field(
        title="URL of the article",
        example="https://en.wikipedia.org/wiki/Python_(programming_language)",
    )
    title: str = Field(
        title="Title of the article", example="Python (programming language)"
    )
    summary: str = Field(
        title="Summary of the article",
        example="Python is a high-level, interpreted programming language...",
    )
    model_used: str = Field(
        title="Model used to generate the summary", example="deepseek"
    )
    created_at: datetime = Field(
        title="Date and time of creation", example="2024-01-15T10:30:00Z"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
                "title": "Python (programming language)",
                "summary": "Python is a high-level, interpreted programming language...",
                "model_used": "deepseek",
                "created_at": "2024-01-15T10:30:00Z",
            }
        }
    }
