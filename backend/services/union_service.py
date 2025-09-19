from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from backend import models, schemas
from backend.repositories.union_repository import UnionRepository

class UnionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.union_repo = UnionRepository(db)

    async def get_unions_by_user(self, user_id: int) -> List[models.Union]:
        """根据用户ID获取公会列表"""
        return await self.union_repo.get_by_user_id(user_id)

    async def create_union(self, union: schemas.UnionCreate, user_id: int) -> models.Union:
        """为用户创建一个新公会"""
        db_union = models.Union(name=union.name, user_id=user_id)
        return await self.union_repo.create(db_union)

    async def update_union(self, union_id: int, name: str, user_id: int) -> Optional[models.Union]:
        """更新公会信息"""
        db_union = await self.union_repo.get_by_id_and_user_id(union_id, user_id)
        if db_union:
            return await self.union_repo.update(db_union, {"name": name})
        return None

    async def delete_union(self, union_id: int, user_id: int) -> bool:
        """删除一个公会"""
        db_union = await self.union_repo.get_by_id_and_user_id(union_id, user_id)
        if db_union:
            if db_union.players:
                # 或者在这里引发一个特定的业务逻辑异常
                return False  # 或者 True/False 表示是否能删除
            await self.union_repo.remove(id=db_union.id)
            return True
        return False
