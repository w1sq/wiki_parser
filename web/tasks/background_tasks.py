import asyncio
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from web.db.models import ArticleStorage, ArticleSummaryStorage
from web.db.connection.session import SessionManager
from web.utils.groq_summary import get_summary
from web.utils.wikiparse import get_article_text, get_article_title, get_linked_articles


def _get_session_maker():
    """Get session maker from the session manager"""
    return SessionManager().get_session_maker()


async def parse_article_background(
    article_id: int, url: str, parent_id: Optional[int] = None, level: int = 0
) -> None:
    """
    Background task для парсинга статьи Wikipedia с рекурсивным парсингом связанных статей
    """
    try:
        session_maker = _get_session_maker()
        async with session_maker() as session:
            update_query = (
                update(ArticleStorage)
                .where(ArticleStorage.id == article_id)
                .values(status="processing")
            )
            await session.execute(update_query)
            await session.commit()

            article_text = get_article_text(url)
            article_title = get_article_title(url)

            if not article_text:
                raise Exception(f"Could not parse article content for {url}")

            update_query = (
                update(ArticleStorage)
                .where(ArticleStorage.id == article_id)
                .values(
                    title=article_title or "Unknown Title",
                    content=article_text,
                    status="completed",
                )
            )
            await session.execute(update_query)
            await session.commit()

            await generate_summary_background(article_id, article_text)

            if level < 5:
                linked_articles = get_linked_articles(url, max_links=5)

                for linked_article in linked_articles:
                    existing_query = select(ArticleStorage).where(
                        ArticleStorage.url == linked_article["url"]
                    )
                    existing = await session.scalar(existing_query)

                    if not existing:
                        new_linked_article = ArticleStorage(
                            url=linked_article["url"],
                            title=linked_article["title"],
                            content=linked_article["content"],
                            status="completed",
                            level=level + 1,
                            parent_id=article_id,
                        )
                        session.add(new_linked_article)
                        await session.commit()
                        await session.refresh(new_linked_article)

                        await generate_summary_background(
                            new_linked_article.id, linked_article["content"]
                        )

            print(f"Article {url} parsed successfully (level: {level})")

    except Exception as e:
        session_maker = _get_session_maker()
        async with session_maker() as session:
            update_query = (
                update(ArticleStorage)
                .where(ArticleStorage.id == article_id)
                .values(status="failed")
            )
            await session.execute(update_query)
            await session.commit()

        print(f"Error parsing article {url}: {str(e)}")
        raise


async def generate_summary_background(article_id: int, content: str) -> None:
    """
    Background task для генерации summary статьи
    """
    try:
        session_maker = _get_session_maker()
        async with session_maker() as session:
            existing_summary_query = select(ArticleSummaryStorage).where(
                ArticleSummaryStorage.article_id == article_id
            )
            existing_summary = await session.scalar(existing_summary_query)

            if existing_summary:
                print(f"Summary for article {article_id} already exists")
                return

            summary_text = get_summary(content)

            new_summary = ArticleSummaryStorage(
                article_id=article_id,
                text=summary_text,
                model_used="groq-gemma2-9b-it",
            )
            session.add(new_summary)
            await session.commit()
            await session.refresh(new_summary)

            print(f"Summary generated for article {article_id}")

    except Exception as e:
        print(f"Error generating summary for article {article_id}: {str(e)}")
        raise


def parse_article_background_sync(
    article_id: int, url: str, parent_id: Optional[int] = None, level: int = 0
) -> None:
    """
    Синхронная обертка для parse_article_background
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            parse_article_background(article_id, url, parent_id, level)
        )
    finally:
        loop.close()


def generate_summary_background_sync(article_id: int, content: str) -> None:
    """
    Синхронная обертка для generate_summary_background
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_summary_background(article_id, content))
    finally:
        loop.close()
