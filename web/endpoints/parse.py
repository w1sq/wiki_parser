from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from web.db.connection import get_session
from web.db.models import ArticleStorage
from web.schemas import ParseRequest, ParseResponse
from web.tasks.background_tasks import parse_article_background_sync


api_router = APIRouter()


@api_router.post(
    "/parse",
    response_model=ParseResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid URL or article already exists",
        },
    },
)
async def parse_article(
    background_tasks: BackgroundTasks,
    model: ParseRequest = Body(
        ...,
        example={"url": "https://en.wikipedia.org/wiki/Python_(programming_language)"},
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Запуск парсинга статьи по URL. Использует FastAPI background tasks.

    Логика:
    1. Проверяем, что статья еще не парсилась
    2. Создаем запись в БД со статусом "pending"
    3. Добавляем background task для парсинга
    4. Возвращаем article_id для отслеживания
    """
    existing_article_query = select(ArticleStorage).where(
        ArticleStorage.url == str(model.url)
    )
    existing_article = await session.scalar(existing_article_query)

    if existing_article:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article already exists in database",
        )

    new_article = ArticleStorage(
        url=str(model.url),
        title="",  # Будет заполнено после парсинга
        content="",  # Будет заполнено после парсинга
        status="pending",  # pending, processing, completed, failed
        level=0,  # Уровень вложенности (0 для исходной статьи)
    )
    session.add(new_article)
    await session.commit()
    await session.refresh(new_article)

    background_tasks.add_task(
        parse_article_background_sync,
        article_id=new_article.id,
        url=str(model.url),
        parent_id=None,
        level=0,
    )

    return ParseResponse(
        task_id=f"background_task_{new_article.id}",
        article_id=new_article.id,
        url=str(model.url),
        status="pending",
    )
