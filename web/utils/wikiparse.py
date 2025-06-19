from typing import Optional, Dict, List

import wikipediaapi


def get_article_name(url: str) -> str:
    """Extract article name from Wikipedia URL"""
    return url.split("/wiki/")[-1]


def _get_wikipedia_client() -> wikipediaapi.Wikipedia:
    """Get a configured Wikipedia API client"""
    return wikipediaapi.Wikipedia(
        user_agent="Wikipedia Parser (example@example.com)", language="en"
    )


def _get_page(url: str) -> Optional[wikipediaapi.WikipediaPage]:
    """Get Wikipedia page object for a given URL"""
    article_name = get_article_name(url)
    wiki_wiki = _get_wikipedia_client()
    page = wiki_wiki.page(article_name)

    if not page.text:
        return None

    return page


def get_article_text(url: str) -> Optional[str]:
    """Get the text content of a Wikipedia article"""
    page = _get_page(url)
    return page.text if page else None


def get_article_title(url: str) -> Optional[str]:
    """Get the title of a Wikipedia article"""
    page = _get_page(url)
    return page.title if page else None


def get_linked_articles(url: str, max_links: int = 5) -> List[Dict[str, str]]:
    """Get linked articles from a Wikipedia page"""
    page = _get_page(url)
    if not page:
        return []

    linked_articles = []
    i = 0
    for title, linked_page in page.links.items():
        if i >= max_links:
            break

        if linked_page.text:
            linked_articles.append(
                {
                    "title": title,
                    "url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                    "content": linked_page.text,
                }
            )
            i += 1

    return linked_articles


def parse_article(url: str) -> Optional[dict[str, str]]:
    """
    Parse a Wikipedia article and return a dictionary with title and content.
    This function is kept for backward compatibility but uses the new structure.
    """
    page = _get_page(url)
    if not page:
        return None

    pages = {page.title: page.text}

    linked_articles = get_linked_articles(url, max_links=5)
    for article in linked_articles:
        pages[article["title"]] = article["content"]

    return pages
