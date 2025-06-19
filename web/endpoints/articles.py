from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from web.db.connection import get_session
from web.db.models import ArticleStorage
from web.schemas import ArticleStatusResponse

api_router = APIRouter()


@api_router.get(
    "/articles/{article_id}/status",
    response_model=ArticleStatusResponse,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Article not found"}},
)
async def get_article_status(
    article_id: int = Path(..., description="Article ID"),
    session: AsyncSession = Depends(get_session),
):
    """
    Получить статус парсинга статьи по article_id
    """
    article_query = select(ArticleStorage).where(ArticleStorage.id == article_id)
    article = await session.scalar(article_query)

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with id {article_id} not found",
        )

    return ArticleStatusResponse(
        article_id=article.id,
        url=article.url,
        title=article.title,
        status=article.status,
        level=article.level,
        created_at=article.created_at,
        updated_at=article.updated_at,
    )
