"""SQLAlchemy base and model registry."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models so Alembic can detect them
from app.models.user import User  # noqa: F401, E402
from app.models.paper import Paper, AISummary  # noqa: F401, E402
from app.models.collection import Collection, CollectionPaper  # noqa: F401, E402
from app.models.search_history import SearchHistory  # noqa: F401, E402
