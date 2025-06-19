from datetime import datetime
from pydantic import BaseModel, Field


class TaskResponse(BaseModel):
    """Схема для ответа с информацией о задаче"""

    task_id: str = Field(title="ID of the task", example="parse_task_123")
    status: str = Field(
        title="Status of the task",
        example="pending",
        description="pending, processing, completed, failed",
    )
    created_at: datetime = Field(
        title="Date and time of creation", example="2024-01-15T10:30:00Z"
    )
    updated_at: datetime = Field(
        title="Date and time of last update", example="2024-01-15T10:30:00Z"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "task_id": "parse_task_123",
                "status": "pending",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
            }
        }
    }
