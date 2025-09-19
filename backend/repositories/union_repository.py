from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from backend import models, schemas
from backend.repositories.base import BaseRepository

class UnionRepository(BaseRepository[models.Union, schemas.UnionCreate, schemas.UnionUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(models.Union)
        self.db = db

    async def get_by_user_id(self, user_id: int) -> List[models.Union]:
        result = await self.db.execute(select(self.model).filter(self.model.user_id == user_id))
        return result.scalars().all()

    async def get_by_id_and_user_id(self, union_id: int, user_id: int) -> Optional[models.Union]:
        result = await self.db.execute(
            select(self.model).filter(
                self.model.id == union_id,
                self.model.user_id == user_id
            )
        )
        return result.scalars().first()