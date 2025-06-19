from uuid import UUID

from pydantic import BaseModel, HttpUrl, Field


class ParseRequest(BaseModel):
    """Схема для запроса на парсинг статьи"""

    url: HttpUrl = Field(
        title="URL of the article to parse",
        example="https://en.wikipedia.org/wiki/Python_(programming_language)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://en.wikipedia.org/wiki/Python_(programming_language)"
            }
        }
    }


class ParseResponse(BaseModel):
    """Схема для ответа на запрос парсинга"""

    task_id: str = Field(title="ID of the task", example="parse_task_123")
    article_id: UUID = Field(
        title="ID of the article", example="123e4567-e89b-12d3-a456-426614174000"
    )
    url: str = Field(
        title="URL of the article",
        example="https://en.wikipedia.org/wiki/Python_(programming_language)",
    )
    status: str = Field(title="Status of the task", example="pending")

    model_config = {
        "json_schema_extra": {
            "example": {
                "task_id": "parse_task_123",
                "article_id": "123e4567-e89b-12d3-a456-426614174000",
                "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
                "status": "pending",
            }
        }
    }
