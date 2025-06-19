from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Request,
    Query,
    BackgroundTasks,
)
from fastapi.responses import RedirectResponse
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from web.db.connection import get_session
from web.db.models import ArticleStorage, ArticleSummaryStorage
from web.schemas import SummaryResponse
from web.tasks.background_tasks import generate_summary_background_sync


api_router = APIRouter()


@api_router.get(
    "/summary",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Summary for this URL not found"}
    },
)
async def get_article_summary(
    url: str = Query(..., description="URL of the article"),
    session: AsyncSession = Depends(get_session),
):
    """
    Получить summary для статьи по url. Если summary нет — 404.
    """
    # Найти статью по url
    article_query = select(ArticleStorage).where(ArticleStorage.url == url)
    article = await session.scalar(article_query)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with url '{url}' not found",
        )
    # Найти summary для этой статьи
    summary_query = select(ArticleSummaryStorage).where(
        ArticleSummaryStorage.article_id == article.id
    )
    summary = await session.scalar(summary_query)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Summary for article '{url}' not found",
        )
    return SummaryResponse(
        url=article.url,
        title=article.title,
        summary=summary.text,
        model_used=summary.model_used,
        created_at=summary.created_at,
    )


@api_router.post(
    "/summary/generate",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Article not found"},
        status.HTTP_400_BAD_REQUEST: {"description": "Summary already exists"},
    },
)
async def generate_article_summary(
    background_tasks: BackgroundTasks,
    url: str = Query(..., description="URL of the article"),
    session: AsyncSession = Depends(get_session),
):
    """
    Запустить генерацию summary для статьи по URL. Использует FastAPI background tasks.
    """
    # Найти статью по url
    article_query = select(ArticleStorage).where(ArticleStorage.url == url)
    article = await session.scalar(article_query)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with url '{url}' not found",
        )

    # Проверяем, что summary еще не существует
    summary_query = select(ArticleSummaryStorage).where(
        ArticleSummaryStorage.article_id == article.id
    )
    existing_summary = await session.scalar(summary_query)
    if existing_summary:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Summary for article '{url}' already exists",
        )

    # Добавляем background task для генерации summary
    background_tasks.add_task(
        generate_summary_background_sync,
        article_id=article.id,
        content=article.content,
    )

    return {
        "message": f"Summary generation started for article '{url}'",
        "article_id": str(article.id),
        "status": "pending",
    }
