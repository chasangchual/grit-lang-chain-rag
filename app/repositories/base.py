from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic base repository with common CRUD operations."""

    def __init__(self, session: Session, model: type[ModelType]):
        self.session = session
        self.model = model

    def get_by_id(self, id: int) -> ModelType | None:
        """Get a record by its internal ID."""
        return self.session.get(self.model, id)

    def get_by_public_id(self, public_id: UUID) -> ModelType | None:
        """Get a record by its public UUID."""
        stmt = select(self.model).where(self.model.public_id == public_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Get all records with pagination."""
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def count(self) -> int:
        """Count total number of records."""
        stmt = select(func.count()).select_from(self.model)
        return self.session.execute(stmt).scalar() or 0

    def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        self.session.flush()
        return instance

    def update(self, instance: ModelType, **kwargs) -> ModelType:
        """Update an existing record."""
        for key, value in kwargs.items():
            if value is not None:
                setattr(instance, key, value)
        self.session.flush()
        return instance

    def delete(self, instance: ModelType) -> bool:
        """Delete a record."""
        self.session.delete(instance)
        self.session.flush()
        return True

    def delete_by_public_id(self, public_id: UUID) -> bool:
        """Delete a record by its public UUID."""
        instance = self.get_by_public_id(public_id)
        if instance:
            return self.delete(instance)
        return False
