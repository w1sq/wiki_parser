from web.endpoints.parse import api_router as parse_router
from web.endpoints.summary import api_router as summary_router


list_of_routes = [
    parse_router,
    summary_router,
]


__all__ = [
    "list_of_routes",
]
