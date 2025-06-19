from setuptools import setup, find_packages

setup(
    name="web",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi[standard]==0.115.13",
        "uvicorn[standard]==0.34.3",
        "pydantic-settings==2.9.1",
        "groq==0.28.0",
        "wikipedia-api==0.8.1",
        "sqlalchemy[asyncio]==2.0.41",
        "asyncpg==0.30.0",
        "alembic==1.16.2",
        "psycopg2-binary==2.9.10",
    ],
)
