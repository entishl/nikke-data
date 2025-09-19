from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update
import json
import logging
from typing import List, Optional, Dict, Any
from backend import models, schemas, constants
from backend.repositories.user_repository import UserRepository
from backend.utils import get_password_hash
from backend.utils import NIKKE_LIST_DATA
from backend.core import simulation
from backend.core.simulation import CharacterStats, PlayerForSim

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_user_by_username(self, username: str) -> Optional[models.User]:
        """根据用户名查询用户"""
        return await self.user_repo.get_by_username(username)

    async def create_user(self, user: schemas.UserCreate) -> Optional[models.User]:
        """创建一个新用户，并处理密码"""
        db_user = await self.get_user_by_username(user.username)
        if db_user:
            return None
        hashed_password = get_password_hash(user.password)
        new_user = models.User(username=user.username, hashed_password=hashed_password)
        return await self.user_repo.create(new_user)

    async def update_or_create_player(self, player_name: str, synchro_level: int, resilience_cube_level: int, bastion_cube_level: int, union_id: int = None, user_id: int = None) -> models.Player:
        """
        Updates an existing player or creates a new one.
        Also deletes old character data for the player to ensure a clean sync.
        """
        player = await self.user_repo.get_player_by_name_and_user_id(player_name, user_id)

        if not player:
            player_data = schemas.PlayerCreate(
                name=player_name,
                synchro_level=synchro_level,
                resilience_cube_level=resilience_cube_level,
                bastion_cube_level=bastion_cube_level,
                union_id=union_id,
                user_id=user_id
            )
            return await self.user_repo.create_player(player_data)
        else:
            update_data = schemas.PlayerUpdate(
                synchro_level=synchro_level,
                resilience_cube_level=resilience_cube_level,
                bastion_cube_level=bastion_cube_level,
                union_id=union_id
            )
            updated_player = await self.user_repo.update_player(player, update_data)
            # Delete old character data for this player to re-sync
            await self.db.execute(delete(models.Character).where(models.Character.player_id == updated_player.id))
            await self.db.commit()
            return updated_player

    async def get_characters_with_details(
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
    ) -> List[schemas.CharacterResponse]:
        """
        Retrieves and filters characters, then formats them for the API response.
        """
        characters = await self.user_repo.get_characters(
            user_id=user_id,
            player_name=player_name,
            union_ids=union_ids,
            character_name=character_name,
            class_=class_,
            element=element,
            weapon_type=weapon_type,
            use_burst_skill=use_burst_skill,
            sort_by=sort_by,
            order=order
        )
        
        result = []
        for char in characters:
            grade = char.limit_break_grade or 0
            core = char.core or 0
            breakthrough_coefficient = 1 + (grade * constants.LIMIT_BREAK_GRADE_COEFFICIENT) + (core * constants.CORE_ENHANCEMENT_COEFFICIENT)
            
            response_data = schemas.CharacterResponse(
                id=char.id,
                player_name=char.player.name if char.player else None,
                union_id=char.player.union_id if char.player else None,
                union_name=char.player.union.name if char.player and char.player.union else None,
                character_id=char.character_id,
                name_cn=char.name_cn,
                element=char.element,
                element_from_user=char.element_from_user,
                skill1_level=char.skill1_level,
                skill2_level=char.skill2_level,
                skill_burst_level=char.skill_burst_level,
                limit_break_grade=char.limit_break_grade,
                core=char.core,
                item_level=char.item_level,
                item_rare=char.item_rare,
                total_stat_atk=char.total_stat_atk,
                total_inc_element_dmg=char.total_inc_element_dmg,
                total_stat_ammo_load=char.total_stat_ammo_load,
                total_superiority=char.total_superiority,
                absolute_training_degree=char.absolute_training_degree,
                relative_training_degree=char.relative_training_degree,
                general_relative_training_degree=char.general_relative_training_degree,
                class_=char.class_,
                corporation=char.corporation,
                weapon_type=char.weapon_type,
                original_rare=char.original_rare,
                use_burst_skill=char.use_burst_skill,
                is_C=char.is_C,
                breakthrough_coefficient=breakthrough_coefficient
            )
            result.append(response_data)
            
        return result

    async def get_all_unique_characters(self) -> List[Dict[str, Any]]:
        """Gets all unique characters from the database."""
        query = await self.db.execute(select(models.Character.character_id, models.Character.name_cn, models.Character.element, models.Character.element_from_user).distinct())
        unique_characters = [
            {"id": char_id, "name_cn": name_cn, "element": element, "element_from_user": element_from_user}
            for char_id, name_cn, element, element_from_user in query.all()
        ]
        return sorted(unique_characters, key=lambda x: x['id'])

    async def get_is_c_settings(self) -> Dict[int, bool]:
        """Gets all CharacterSetting 'is_C' values."""
        result = await self.db.execute(select(models.CharacterSetting))
        settings = result.scalars().all()
        return {setting.character_id: setting.is_C for setting in settings}

    async def update_is_c_settings(self, settings: Dict[int, bool]) -> None:
        """Updates 'is_C' settings for characters."""
        for char_id, is_c in settings.items():
            result = await self.db.execute(select(models.CharacterSetting).filter_by(character_id=char_id))
            setting = result.scalars().first()
            if setting:
                setting.is_C = is_c
            else:
                setting = models.CharacterSetting(character_id=char_id, is_C=is_c)
                self.db.add(setting)
            
            await self.db.execute(
                update(models.Character).where(models.Character.character_id == char_id).values(is_C=is_c)
            )
        await self.db.commit()

    async def get_character_details(self, character_db_id: int) -> Optional[Dict[str, Any]]:
        """Gets detailed information for a single character."""
        char = await self.user_repo.get_character_by_id(character_db_id)
        if not char:
            return None

        equipments = [{
            "equipment_slot": equip.equipment_slot,
            "function_type": equip.function_type,
            "function_value": equip.function_value,
            "level": equip.level,
        } for equip in char.equipments]

        grade = char.limit_break_grade or 0
        core = char.core or 0
        breakthrough_coefficient = 1 + (grade * constants.LIMIT_BREAK_GRADE_COEFFICIENT) + (core * constants.CORE_ENHANCEMENT_COEFFICIENT)

        return {
            "id": char.id,
            "player_name": char.player.name,
            "character_id": char.character_id,
            "name_cn": char.name_cn,
            "element": char.element,
            "element_from_user": char.element_from_user,
            "skill1_level": char.skill1_level,
            "skill2_level": char.skill2_level,
            "skill_burst_level": char.skill_burst_level,
            "limit_break_grade": char.limit_break_grade,
            "core": char.core,
            "item_level": char.item_level,
            "item_rare": char.item_rare,
            "equipments": equipments,
            "total_stat_atk": char.total_stat_atk,
            "total_inc_element_dmg": char.total_inc_element_dmg,
            "total_stat_ammo_load": char.total_stat_ammo_load,
            "total_superiority": char.total_superiority,
            "absolute_training_degree": char.absolute_training_degree,
            "relative_training_degree": char.relative_training_degree,
            "general_relative_training_degree": char.general_relative_training_degree,
            "breakthrough_coefficient": breakthrough_coefficient,
        }

    async def delete_player_and_data(self, player_name: str, user_id: int) -> bool:
        """Deletes a player and all their associated data."""
        player = await self.user_repo.get_player_by_name_and_user_id(player_name, user_id)
        if not player:
            return False
        
        # Cascade delete is handled by relationships, but explicit is fine
        await self.db.execute(delete(models.Character).where(models.Character.player_id == player.id))
        await self.db.delete(player)
        await self.db.commit()
        return True

    async def clear_all_user_data(self, user_id: int) -> None:
        """Clears all data (players, characters, etc.) associated with a user."""
        result = await self.db.execute(select(models.Player).filter(models.Player.user_id == user_id))
        players = result.scalars().all()
        player_ids = [p.id for p in players]

        if player_ids:
            await self.db.execute(delete(models.Equipment).where(models.Equipment.character.has(models.Character.player_id.in_(player_ids))))
            await self.db.execute(delete(models.Character).where(models.Character.player_id.in_(player_ids)))
            await self.db.execute(delete(models.Player).where(models.Player.id.in_(player_ids)))
        
        await self.db.execute(delete(models.Union).where(models.Union.user_id == user_id))
        
        await self.db.commit()

    async def get_players(self, user_id: int, union_ids: Optional[str] = None, sort_by: str = "name", order: str = "asc") -> List[Dict[str, Any]]:
        """Gets a list of players, optionally filtered by union."""
        players = await self.user_repo.get_players(user_id, union_ids, sort_by, order)
        return [
            {
                "id": player.id,
                "name": player.name,
                "synchro_level": player.synchro_level,
                "resilience_cube_level": player.resilience_cube_level,
                "bastion_cube_level": player.bastion_cube_level,
                "union_id": player.union_id,
                "union_name": player.union.name if player.union else None,
            }
            for player in players
        ]

    async def get_element_training_analysis(self, user_id: int, union_ids: Optional[str], character_coefficients: str, training_type: str) -> List[Dict[str, Any]]:
        """Performs element training analysis."""
        try:
            coeffs = json.loads(character_coefficients)
            character_ids = [int(k) for k in coeffs.keys()]
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError("Invalid character_coefficients format.") from e

        if not character_ids:
            return []

        players = await self.user_repo.get_players(user_id, union_ids)
        if not players:
            return []

        player_ids = [p.id for p in players]
        result = await self.db.execute(
            select(models.Character).filter(
                models.Character.player_id.in_(player_ids),
                models.Character.character_id.in_(character_ids)
            )
        )
        characters = result.scalars().all()

        analysis_results = {
            p.name: {"player_name": p.name, "elements": {el: 0 for el in constants.ELEMENTS}}
            for p in players
        }

        for char in characters:
            coefficient = coeffs.get(str(char.character_id))
            if coefficient is not None:
                training_value = getattr(char, training_type, 0)
                player_name = char.player.name
                if player_name in analysis_results:
                    analysis_results[player_name]["elements"][char.element] += training_value * float(coefficient)

        return list(analysis_results.values())

    def get_filter_options(self) -> Dict[str, List[str]]:
        """Gets unique filter options from NIKKE_LIST_DATA."""
        nikkes = NIKKE_LIST_DATA.get('nikkes', [])
        
        classes = sorted(list(set(n.get('class') for n in nikkes if n.get('class'))))
        elements = sorted(list(set(n.get('element') for n in nikkes if n.get('element'))))
        weapon_types = sorted(list(set(n.get('weapon_type') for n in nikkes if n.get('weapon_type'))))
        use_burst_skills = sorted(list(set(n.get('use_burst_skill') for n in nikkes if n.get('use_burst_skill'))))

        return {
            "class": classes,
            "element": elements,
            "weapon_type": weapon_types,
            "use_burst_skill": use_burst_skills,
        }

    async def process_uploaded_files(self, file_contents: Dict[str, bytes], union_id: Optional[int], user_id: int) -> (int, int):
        """Processes multiple uploaded files."""
        import json

        successful_files = 0
        failed_files = 0

        all_character_ids = set()
        decoded_files = {}
        for filename, contents in file_contents.items():
            try:
                data = json.loads(contents)
                decoded_files[filename] = data
                for element, characters_in_element in data.get("elements", {}).items():
                    for char_data in characters_in_element:
                        if "id" in char_data:
                            char_id = char_data["id"]
                            all_character_ids.add(char_id)
                            if char_id == constants.RED_HOOD_ID:
                                all_character_ids.add(constants.VIRTUAL_RED_HOOD_ID)
            except json.JSONDecodeError:
                failed_files += 1
                logging.warning(f"Failed to decode JSON from file {filename}")
                continue
        
        is_c_settings = {}
        if all_character_ids:
            result = await self.db.execute(select(models.CharacterSetting).filter(models.CharacterSetting.character_id.in_(all_character_ids)))
            settings = result.scalars().all()
            is_c_settings = {setting.character_id: setting.is_C for setting in settings}

        for filename, data in decoded_files.items():
            try:
                await self._process_single_upload_data(data, union_id, is_c_settings, user_id)
                successful_files += 1
            except Exception as e:
                await self.db.rollback()
                failed_files += 1
                logging.error(f"Failed to process file {filename}: {e}", exc_info=True)
        
        return successful_files, failed_files

    async def _process_single_upload_data(self, data: dict, union_id: int, is_c_settings: dict, user_id: int):
        from backend.utils import CUBE_LEVEL_MAP
        player_name = data.get("name")
        if not player_name:
            raise ValueError("Player name not found in data.")

        resilience_cube_level = 0
        bastion_cube_level = 0
        max_cube_level = 0
        for cube in data.get("cubes", []):
            cube_level = cube.get("cube_level", 0)
            if cube_level > max_cube_level:
                max_cube_level = cube_level
            if cube.get("name_cn") == constants.RESILIENCE_CUBE_NAME:
                resilience_cube_level = cube.get("cube_level", 0)
            elif cube.get("name_cn") == constants.BASTION_CUBE_NAME:
                bastion_cube_level = cube.get("cube_level", 0)
        
        cube_superiority_increase = CUBE_LEVEL_MAP.get(max_cube_level, {}).get("IncElementDmg", 0)

        player = await self.update_or_create_player(
            player_name=player_name,
            synchro_level=data.get("synchroLevel"),
            resilience_cube_level=resilience_cube_level,
            bastion_cube_level=bastion_cube_level,
            union_id=union_id,
            user_id=user_id
        )

        for element, characters_in_element in data.get("elements", {}).items():
            for char_data in characters_in_element:
                if 'skill1_level' not in char_data or "id" not in char_data or "name_cn" not in char_data:
                    continue

                coor_level = char_data.get('coor_level', 0)
                attributes = self._calculate_character_attributes(
                    char_data=char_data,
                    sync_level=data.get("synchroLevel", 1),
                    cube_superiority_increase=cube_superiority_increase,
                    max_cube_level=max_cube_level,
                    coor_level=coor_level
                )
                
                await self._create_character_with_equipment(
                    player=player,
                    char_data=char_data,
                    attributes=attributes,
                    element_from_user=element,
                    is_c_settings=is_c_settings
                )

    def _calculate_character_attributes(self, char_data: dict, sync_level: int, cube_superiority_increase: float, max_cube_level: int, coor_level: int = 0):
        from backend.utils import NIKKE_STATIC_DATA, NUMBER_DATA, RANK_DATA, EQUIPMENT_DATA, SUPER_DATA, CUBE_DATA
        from backend.final_attack import calculate_final_attack
        
        total_stat_atk = sum(equip_data.get("function_value", 0) for slot, equipments in char_data.get("equipments", {}).items() for equip_data in equipments if equip_data.get("function_type") == "StatAtk")
        total_inc_element_dmg = sum(equip_data.get("function_value", 0) for slot, equipments in char_data.get("equipments", {}).items() for equip_data in equipments if equip_data.get("function_type") == "IncElementDmg")
        total_stat_ammo_load = sum(equip_data.get("function_value", 0) for slot, equipments in char_data.get("equipments", {}).items() for equip_data in equipments if equip_data.get("function_type") == "StatAmmoLoad")
        
        total_superiority = total_inc_element_dmg + constants.BASE_SUPERIORITY + cube_superiority_increase
        character_id = char_data.get("id")
        static_data = NIKKE_STATIC_DATA.get(character_id, {})
        grade = char_data.get("limit_break", {}).get("grade", 0) or 0
        core = char_data.get("limit_break", {}).get("core", 0) or 0
        breakthrough_coefficient = 1 + (grade * constants.LIMIT_BREAK_GRADE_COEFFICIENT) + (core * constants.CORE_ENHANCEMENT_COEFFICIENT)
        sync_level_idx = sync_level - 1
        char_class = static_data.get("class")
        sync_attack_list_name = f"{char_class}_level_attack_list"
        sync_attack_list = NUMBER_DATA.get(sync_attack_list_name, [])
        sync_attack = sync_attack_list[sync_level_idx] if sync_level_idx < len(sync_attack_list) else 0
        
        final_attack = calculate_final_attack(
            sync_attack=sync_attack, grade=grade, corporation=static_data.get("corporation"),
            character_id=character_id, super_character_ids=SUPER_DATA.get("super", []),
            character_class_en=static_data.get("class"), rank_data=RANK_DATA, coor_level=coor_level,
            equipment_data=EQUIPMENT_DATA, item_rare=char_data.get("item_rare"),
            item_level=char_data.get("item_level", 1), number_data=NUMBER_DATA, core=core,
            cube_level=max_cube_level, cube_data=CUBE_DATA
        )

        relative_training_degree = breakthrough_coefficient * (1 + total_stat_atk / 100) * (1 + total_superiority / 100)
        absolute_training_degree = sync_attack * relative_training_degree
        general_relative_training_degree = breakthrough_coefficient * (1 + total_stat_atk)

        return {
            "total_stat_atk": total_stat_atk, "total_inc_element_dmg": total_inc_element_dmg,
            "total_stat_ammo_load": total_stat_ammo_load, "total_superiority": total_superiority,
            "final_attack": final_attack, "absolute_training_degree": absolute_training_degree,
            "relative_training_degree": relative_training_degree,
            "general_relative_training_degree": general_relative_training_degree,
            "static_data": static_data, "breakthrough_coefficient": breakthrough_coefficient
        }

    async def _create_character_with_equipment(self, player: models.Player, char_data: dict, attributes: dict, element_from_user: str, is_c_settings: dict):
        from backend.utils import NIKKE_STATIC_DATA
        character_id = char_data.get("id")
        static_data = attributes["static_data"]

        new_char_data = {
            "player_id": player.id, "character_id": character_id, "name_cn": char_data.get("name_cn"),
            "element": static_data.get("element"), "element_from_user": element_from_user,
            "skill1_level": char_data.get("skill1_level"), "skill2_level": char_data.get("skill2_level"),
            "skill_burst_level": char_data.get("skill_burst_level"),
            "limit_break_grade": char_data.get("limit_break", {}).get("grade"),
            "core": char_data.get("limit_break", {}).get("core"),
            "item_level": char_data.get("item_level"), "item_rare": char_data.get("item_rare"),
            "total_stat_atk": attributes["total_stat_atk"], "total_inc_element_dmg": attributes["total_inc_element_dmg"],
            "total_stat_ammo_load": attributes["total_stat_ammo_load"], "total_superiority": attributes["total_superiority"],
            "final_attack": attributes["final_attack"], "absolute_training_degree": attributes["absolute_training_degree"],
            "relative_training_degree": attributes["relative_training_degree"],
            "general_relative_training_degree": attributes["general_relative_training_degree"],
            "class_": static_data.get("class"), "corporation": static_data.get("corporation"),
            "weapon_type": static_data.get("weapon_type"), "original_rare": static_data.get("original_rare"),
            "use_burst_skill": static_data.get("use_burst_skill"),
            "is_C": is_c_settings.get(character_id, False) if element_from_user == constants.UTILITY_ELEMENT else is_c_settings.get(character_id, True)
        }
        new_char = models.Character(**new_char_data)
        self.db.add(new_char)
        await self.db.commit()
        await self.db.refresh(new_char)

        for slot, equipments in char_data.get("equipments", {}).items():
            for equip_data in equipments:
                self.db.add(models.Equipment(character_id=new_char.id, equipment_slot=int(slot), **equip_data))
        
        if character_id == constants.RED_HOOD_ID:
            virtual_char_id = constants.VIRTUAL_RED_HOOD_ID
            virtual_static_data = NIKKE_STATIC_DATA.get(virtual_char_id, {})
            if virtual_static_data:
                virtual_char_data = new_char_data.copy()
                virtual_char_data.update({
                    "character_id": virtual_char_id, "name_cn": virtual_static_data.get("name_cn"),
                    "element": virtual_static_data.get("element"), "element_from_user": constants.VIRTUAL_RH_ELEMENT,
                    "class_": virtual_static_data.get("class"), "corporation": virtual_static_data.get("corporation"),
                    "weapon_type": virtual_static_data.get("weapon_type"), "original_rare": virtual_static_data.get("original_rare"),
                    "use_burst_skill": virtual_static_data.get("use_burst_skill"),
                    "is_C": is_c_settings.get(virtual_char_id, True)
                })
                virtual_char = models.Character(**virtual_char_data)
                self.db.add(virtual_char)
                await self.db.commit()
                await self.db.refresh(virtual_char)
                for slot, equipments in char_data.get("equipments", {}).items():
                    for equip_data in equipments:
                        self.db.add(models.Equipment(character_id=virtual_char.id, equipment_slot=int(slot), **equip_data))
        await self.db.commit()

    async def run_damage_simulation(self, request: schemas.DamageSimulationRequest) -> schemas.DamageSimulationResponse:
        # Step 1: Collect all unique character IDs from the request
        all_character_ids = list(set(char.character_id for team in request.teams for char in team.characters))

        # Step 2: Bulk fetch base character stats and convert to DTOs
        base_chars_list = await self.user_repo.get_characters_by_ids_for_player(request.base_player_id, all_character_ids)
        base_chars_map = {
            char.character_id: CharacterStats.model_validate(char)
            for char in base_chars_list
        }

        # Step 3: Calculate attribute weights using the pure function
        att_weights = simulation.calculate_attribute_weights(request.teams, base_chars_map)

        # Step 4: Bulk fetch all players in the union with their relevant characters preloaded
        players_in_union_orm = await self.user_repo.get_players_in_union_with_characters(request.union_id, all_character_ids)

        # Step 5: Convert ORM objects to Pydantic models for the pure simulation function
        players_for_sim = [
            PlayerForSim(
                id=p.id,
                name=p.name,
                characters=[CharacterStats.model_validate(char) for char in p.characters]
            )
            for p in players_in_union_orm
        ]

        # Step 6: Perform simulation using the pure function
        simulation_results = simulation.run_player_simulations(players_for_sim, request.teams, att_weights)
            
        return schemas.DamageSimulationResponse(simulation_results=simulation_results)