from setuptools import setup, find_packages

setup(
    name="ai_moderation_bot",
    version="0.1.0",
    description="A data processing and aggregation platform with user roles",
    author="Dima Moroz",
    author_email="d1m.moroz007@gmail.com",
    url="git@github.com:d1mmm/ai_moderation_bot.git",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "SQLAlchemy",
        "pydantic",
    ],
    entry_points={
        "console_scripts": [
            "start-api=ai_moderation_bot.api:main",
            "start-main=ai_moderation_bot.main:main",
        ]
    },
    python_requires='>=3.8',
)
