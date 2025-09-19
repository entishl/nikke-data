from typing import Optional, List
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend import models, schemas, constants
from backend.models import User, Player, Character
from backend.schemas import UserCreate, UserUpdate, PlayerCreate, PlayerUpdate
from backend.repositories.base import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(User)
        self.db = db

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.username == username))
        return result.scalars().first()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_player_by_name_and_user_id(self, name: str, user_id: int) -> Optional[Player]:
        result = await self.db.execute(
            select(Player).filter(Player.name == name, Player.user_id == user_id)
        )
        return result.scalars().first()

    async def create_player(self, player_data: PlayerCreate) -> Player:
        player = Player(**player_data.dict())
        self.db.add(player)
        await self.db.commit()
        await self.db.refresh(player)
        return player

    async def update_player(self, player: Player, player_data: PlayerUpdate) -> Player:
        for field, value in player_data.dict(exclude_unset=True).items():
            setattr(player, field, value)
        await self.db.commit()
        await self.db.refresh(player)
        return player

    async def get_characters(
        self,
        user_id: int,
        player_name: Optional[str] = None,
        union_ids: Optional[str] = None,
        character_name: Optional[str] = None,
        class_: Optional[str] = None,
        element: Optional[str] = None,
        weapon_type: Optional[str] = None,
        use_burst_skill: Optional[str] = None,
        sort_by: str = "absolute_training_degree",
        order: str = "desc"
    ) -> List[Character]:
        query = select(Character).join(Player).filter(Player.user_id == user_id)
        query = query.options(joinedload(Character.player).joinedload(Player.union))

        if union_ids:
            try:
                union_id_list = [int(uid.strip()) for uid in union_ids.split(',') if uid.strip()]
                if union_id_list:
                    query = query.join(Player).filter(Player.union_id.in_(union_id_list))
            except ValueError:
                raise ValueError("Invalid union_ids format. Must be comma-separated integers.")

        if player_name:
            player_names = [name.strip() for name in player_name.split(',') if name.strip()]
            if player_names:
                query = query.join(Player).filter(Player.name.in_(player_names))

        if character_name:
            query = query.filter(Character.name_cn.contains(character_name))
        if class_:
            query = query.filter(Character.class_ == class_)
        if element:
            query = query.filter(Character.element == element)
        if weapon_type:
            query = query.filter(Character.weapon_type == weapon_type)
        if use_burst_skill:
            query = query.filter(Character.use_burst_skill == use_burst_skill)

        sort_column = getattr(Character, sort_by, None)
        if sort_column is None:
            raise ValueError(f"Invalid sort key: {sort_by}")

        if order == constants.DESC_ORDER:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
            
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_character_by_id(self, character_db_id: int) -> Optional[models.Character]:
        result = await self.db.execute(
            select(models.Character).options(
                joinedload(models.Character.player),
                joinedload(models.Character.equipments)
            ).filter(models.Character.id == character_db_id)
        )
        return result.scalars().first()

    async def get_players(self, user_id: int, union_ids: Optional[str] = None, sort_by: str = "name", order: str = "asc") -> List[models.Player]:
        query = select(models.Player).filter(models.Player.user_id == user_id)
        if union_ids:
            try:
                union_id_list = [int(uid.strip()) for uid in union_ids.split(',') if uid.strip()]
                if union_id_list:
                    query = query.filter(models.Player.union_id.in_(union_id_list))
            except ValueError:
                raise ValueError("Invalid union_ids format. Must be comma-separated integers.")

        sort_column = getattr(models.Player, sort_by, None)
        if sort_column is None:
            raise ValueError(f"Invalid sort key: {sort_by}")

        if order == constants.DESC_ORDER:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
            
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_characters_by_ids_for_player(self, player_id: int, character_ids: List[int]) -> List[Character]:
        """
        Fetches specific characters for a single player.
        """
        if not character_ids:
            return []
        result = await self.db.execute(
            select(Character).filter(
                Character.player_id == player_id,
                Character.character_id.in_(character_ids)
            )
        )
        return result.scalars().all()

    async def get_players_in_union_with_characters(self, union_id: int, character_ids: List[int]) -> List[Player]:
        """
        Fetches all players in a union and preloads their specified characters.
        """
        if not character_ids:
            result = await self.db.execute(select(Player).filter(Player.union_id == union_id))
            return result.scalars().all()

        result = await self.db.execute(
            select(Player).filter(
                Player.union_id == union_id
            ).options(
                selectinload(Player.characters).where(
                    Character.character_id.in_(character_ids)
                )
            )
        )
        return result.scalars().all()
