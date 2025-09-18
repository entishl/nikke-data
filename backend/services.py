import logging
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from backend import models, schemas
from backend.final_attack import calculate_final_attack

def update_or_create_player(db: Session, player_name: str, synchro_level: int, resilience_cube_level: int, bastion_cube_level: int, union_id: int = None):
    """
    Updates an existing player or creates a new one.
    Also deletes old character data for the player to ensure a clean sync.
    """
    player = db.query(models.Player).filter(models.Player.name == player_name).first()

    if not player:
        player = models.Player(
            name=player_name,
            synchro_level=synchro_level,
            resilience_cube_level=resilience_cube_level,
            bastion_cube_level=bastion_cube_level,
            union_id=union_id
        )
        db.add(player)
        db.commit()
        db.refresh(player)
    else:
        player.synchro_level = synchro_level
        player.resilience_cube_level = resilience_cube_level
        player.bastion_cube_level = bastion_cube_level
        player.union_id = union_id
        db.commit()
        # Delete old character data for this player to re-sync
        db.query(models.Character).filter(models.Character.player_id == player.id).delete()
        db.commit()
        
    return player
from backend.utils import NIKKE_STATIC_DATA, NUMBER_DATA, RANK_DATA, EQUIPMENT_DATA, SUPER_DATA

def calculate_character_attributes(char_data: dict, sync_level: int, cube_superiority_increase: float, coor_level: int = 0):
    """
    Calculates various character attributes based on raw data and static game data.
    Returns a dictionary of calculated attributes.
    """
    total_stat_atk = 0
    total_inc_element_dmg = 0
    total_stat_ammo_load = 0

    for slot, equipments in char_data.get("equipments", {}).items():
        for equip_data in equipments:
            if equip_data.get("function_type") == "StatAtk":
                total_stat_atk += equip_data.get("function_value", 0)
            elif equip_data.get("function_type") == "IncElementDmg":
                total_inc_element_dmg += equip_data.get("function_value", 0)
            elif equip_data.get("function_type") == "StatAmmoLoad":
                total_stat_ammo_load += equip_data.get("function_value", 0)
    
    total_superiority = total_inc_element_dmg + 10 + cube_superiority_increase

    character_id = char_data.get("id")
    static_data = NIKKE_STATIC_DATA.get(character_id, {})

    # Calculate breakthrough_coefficient
    grade = char_data.get("limit_break", {}).get("grade", 0) or 0
    core = char_data.get("limit_break", {}).get("core", 0) or 0
    breakthrough_coefficient = 1 + (grade * 0.03) + (core * 0.02)

    # Calculate syncAttack
    sync_level_idx = sync_level - 1  # Adjust for 0-based index
    char_class = static_data.get("class")
    sync_attack_list_name = f"{char_class}_level_attack_list"
    sync_attack_list = NUMBER_DATA.get(sync_attack_list_name, [])
    sync_attack = sync_attack_list[sync_level_idx] if sync_level_idx < len(sync_attack_list) else 0
    
    # Calculate itemAttack
    item_rare = char_data.get("item_rare")
    item_level_idx = char_data.get("item_level", 1) - 1  # Adjust for 0-based index
    item_attack = 0
    if item_rare == "SSR":
        item_attack = 9688
    elif item_rare == "SR":
        item_atk_list = NUMBER_DATA.get("item_atk", [])
        item_attack = item_atk_list[item_level_idx] if item_level_idx < len(item_atk_list) else 0

    # Calculate final_attack
    final_attack = calculate_final_attack(
        sync_attack=sync_attack,
        grade=grade,
        corporation=static_data.get("corporation"),
        character_id=character_id,
        super_character_ids=SUPER_DATA.get("super", []),
        character_class_en=static_data.get("class"),
        rank_data=RANK_DATA,
        coor_level=coor_level,
        equipment_data=EQUIPMENT_DATA,
        item_rare=item_rare,
        item_level=char_data.get("item_level", 1),
        number_data=NUMBER_DATA,
        core=core
    )

    # Calculate relative_training_degree and absolute_training_degree
    relative_training_degree = breakthrough_coefficient * (1 + total_stat_atk / 100) * (1 + total_superiority / 100)
    absolute_training_degree = sync_attack * relative_training_degree
    general_relative_training_degree = breakthrough_coefficient * (1 + total_stat_atk)

    return {
        "total_stat_atk": total_stat_atk,
        "total_inc_element_dmg": total_inc_element_dmg,
        "total_stat_ammo_load": total_stat_ammo_load,
        "total_superiority": total_superiority,
        "final_attack": final_attack,
        "absolute_training_degree": absolute_training_degree,
        "relative_training_degree": relative_training_degree,
        "general_relative_training_degree": general_relative_training_degree,
        "static_data": static_data,
        "breakthrough_coefficient": breakthrough_coefficient
    }
def create_character_with_equipment(db: Session, player: models.Player, char_data: dict, attributes: dict, element_from_user: str, is_c_settings: dict):
    """
    Creates a character and its associated equipment in the database.
    Handles special character logic like Rapi: Red Hood.
    """
    character_id = char_data.get("id")
    static_data = attributes["static_data"]

    new_char = models.Character(
        player_id=player.id,
        character_id=character_id,
        name_cn=char_data.get("name_cn"),
        element=static_data.get("element"),
        element_from_user=element_from_user,
        skill1_level=char_data.get("skill1_level"),
        skill2_level=char_data.get("skill2_level"),
        skill_burst_level=char_data.get("skill_burst_level"),
        limit_break_grade=char_data.get("limit_break", {}).get("grade"),
        core=char_data.get("limit_break", {}).get("core"),
        item_level=char_data.get("item_level"),
        item_rare=char_data.get("item_rare"),
        total_stat_atk=attributes["total_stat_atk"],
        total_inc_element_dmg=attributes["total_inc_element_dmg"],
        total_stat_ammo_load=attributes["total_stat_ammo_load"],
        total_superiority=attributes["total_superiority"],
        final_attack=attributes["final_attack"],
        absolute_training_degree=attributes["absolute_training_degree"],
        relative_training_degree=attributes["relative_training_degree"],
        general_relative_training_degree=attributes["general_relative_training_degree"],
        class_=static_data.get("class"),
        corporation=static_data.get("corporation"),
        weapon_type=static_data.get("weapon_type"),
        original_rare=static_data.get("original_rare"),
        use_burst_skill=static_data.get("use_burst_skill"),
        is_C=is_c_settings.get(character_id, False) if element_from_user == 'Utility' else is_c_settings.get(character_id, True)
    )
    db.add(new_char)
    db.commit()
    db.refresh(new_char)

    for slot, equipments in char_data.get("equipments", {}).items():
        for equip_data in equipments:
            new_equip = models.Equipment(
                character_id=new_char.id,
                equipment_slot=int(slot),
                function_type=equip_data.get("function_type"),
                function_value=equip_data.get("function_value"),
                level=equip_data.get("level"),
            )
            db.add(new_equip)
    
    # If the character is "Rapi: Red Hood", create a virtual copy with "Iron" element
    if character_id == 201601:
        virtual_char_id = 201602
        virtual_static_data = NIKKE_STATIC_DATA.get(virtual_char_id, {})
        if virtual_static_data:
            virtual_char = models.Character(
                player_id=player.id,
                character_id=virtual_char_id,
                name_cn=virtual_static_data.get("name_cn"),
                element=virtual_static_data.get("element"),
                element_from_user="Iron",
                skill1_level=char_data.get("skill1_level"),
                skill2_level=char_data.get("skill2_level"),
                skill_burst_level=char_data.get("skill_burst_level"),
                limit_break_grade=char_data.get("limit_break", {}).get("grade"),
                core=char_data.get("limit_break", {}).get("core"),
                item_level=char_data.get("item_level"),
                item_rare=char_data.get("item_rare"),
                total_stat_atk=attributes["total_stat_atk"],
                total_inc_element_dmg=attributes["total_inc_element_dmg"],
                total_stat_ammo_load=attributes["total_stat_ammo_load"],
                total_superiority=attributes["total_superiority"],
                final_attack=attributes["final_attack"],
                absolute_training_degree=attributes["absolute_training_degree"],
                relative_training_degree=attributes["relative_training_degree"],
                general_relative_training_degree=attributes["general_relative_training_degree"],
                class_=virtual_static_data.get("class"),
                corporation=virtual_static_data.get("corporation"),
                weapon_type=virtual_static_data.get("weapon_type"),
                original_rare=virtual_static_data.get("original_rare"),
                use_burst_skill=virtual_static_data.get("use_burst_skill"),
                is_C=is_c_settings.get(virtual_char_id, True)
            )
            db.add(virtual_char)
            db.commit()
            db.refresh(virtual_char)

            for slot, equipments in char_data.get("equipments", {}).items():
                for equip_data in equipments:
                    new_equip = models.Equipment(
                        character_id=virtual_char.id,
                        equipment_slot=int(slot),
                        function_type=equip_data.get("function_type"),
                        function_value=equip_data.get("function_value"),
                        level=equip_data.get("level"),
                    )
                    db.add(new_equip)
    db.commit()
from backend.utils import CUBE_LEVEL_MAP

def process_upload_data(db: Session, data: dict, union_id: int, is_c_settings: dict):
    """
    Processes the entire data from a single uploaded file.
    """
    player_name = data.get("name")
    if not player_name:
        raise ValueError("Player name not found in data.")

    # Extract cube levels and find the max cube level
    resilience_cube_level = 0
    bastion_cube_level = 0
    max_cube_level = 0
    for cube in data.get("cubes", []):
        cube_level = cube.get("cube_level", 0)
        if cube_level > max_cube_level:
            max_cube_level = cube_level
        if cube.get("name_cn") == "遗迹巨熊魔方":
            resilience_cube_level = cube.get("cube_level", 0)
        elif cube.get("name_cn") == "战术巨熊魔方":
            bastion_cube_level = cube.get("cube_level", 0)
    
    cube_superiority_increase = CUBE_LEVEL_MAP.get(max_cube_level, {}).get("IncElementDmg", 0)

    player = update_or_create_player(
        db,
        player_name=player_name,
        synchro_level=data.get("synchroLevel"),
        resilience_cube_level=resilience_cube_level,
        bastion_cube_level=bastion_cube_level,
        union_id=union_id
    )

    for element, characters_in_element in data.get("elements", {}).items():
        for char_data in characters_in_element:
            if "id" not in char_data or "name_cn" not in char_data:
                continue

            coor_level = char_data.get('coor_level', 0)
            attributes = calculate_character_attributes(
                char_data=char_data,
                sync_level=data.get("synchroLevel", 1),
                cube_superiority_increase=cube_superiority_increase,
                coor_level=coor_level
            )
            
            create_character_with_equipment(
                db=db,
                player=player,
                char_data=char_data,
                attributes=attributes,
                element_from_user=element,
                is_c_settings=is_c_settings
            )


def get_characters_service(
   db: Session,
   player_name: Optional[str] = None,
   union_ids: Optional[str] = None,
   character_name: Optional[str] = None,
   class_: Optional[str] = None,
   element: Optional[str] = None,
   weapon_type: Optional[str] = None,
   use_burst_skill: Optional[str] = None,
   sort_by: str = "absolute_training_degree",
   order: str = "desc"
) -> List[models.Character]:
   """
   Retrieves and filters characters from the database.
   """
   query = db.query(models.Character).options(joinedload(models.Character.player).joinedload(models.Player.union))

   if union_ids:
       try:
           union_id_list = [int(uid.strip()) for uid in union_ids.split(',') if uid.strip()]
           if union_id_list:
               query = query.join(models.Player).filter(models.Player.union_id.in_(union_id_list))
       except ValueError:
           # Let the caller handle the HTTPException
           raise ValueError("Invalid union_ids format. Must be comma-separated integers.")

   if player_name:
       player_names = [name.strip() for name in player_name.split(',') if name.strip()]
       if player_names:
           # Ensure we join Player to filter by name
           query = query.join(models.Player).filter(models.Player.name.in_(player_names))

   if character_name:
       query = query.filter(models.Character.name_cn.contains(character_name))
   if class_:
       query = query.filter(models.Character.class_ == class_)
   if element:
       query = query.filter(models.Character.element == element)
   if weapon_type:
       query = query.filter(models.Character.weapon_type == weapon_type)
   if use_burst_skill:
       query = query.filter(models.Character.use_burst_skill == use_burst_skill)

   sort_column = getattr(models.Character, sort_by, None)
   if sort_column is None:
       raise ValueError(f"Invalid sort key: {sort_by}")

   if order == "desc":
       query = query.order_by(sort_column.desc())
   else:
       query = query.order_by(sort_column.asc())
       
   return query.all()

def run_damage_simulation(db: Session, request: schemas.DamageSimulationRequest) -> schemas.DamageSimulationResponse:
    """
    Runs the damage simulation based on the provided request data.
    1. Calculates the 'att_weight' for each character in the base player's teams.
    2. Fetches all players in the specified union.
    3. For each player, calculates the simulated damage for each character.
    4. Assembles and returns the simulation results.
    """
    # Step 1: Calculate att_weight for each base character
    att_weights = {}
    for team in request.teams:
        for char_input in team.characters:
            base_char_stats = db.query(models.Character).filter(
                models.Character.player_id == request.base_player_id,
                models.Character.character_id == char_input.character_id
            ).first()

            if not base_char_stats:
                continue

            # Avoid division by zero
            if not base_char_stats.final_attack or not base_char_stats.total_stat_atk:
                att_weights[char_input.character_id] = 0
                continue

            # Determine element_weight
            element_weight = 1 if base_char_stats.element == team.element else 0
            
            # Unwind the formula to find att_weight
            # damage = final_attack * (1 + total_stat_atk) * (1 + element_weight * total_superiority) * att_weight
            
            superiority_multiplier = 1 + (element_weight * (base_char_stats.total_superiority or 0) / 100)
            attack_multiplier = 1 + ((base_char_stats.total_stat_atk or 0) / 100)

            # Handle potential division by zero
            denominator = base_char_stats.final_attack * superiority_multiplier * attack_multiplier
            if denominator == 0:
                att_weights[char_input.character_id] = 0
                continue

            # Perform the calculation
            try:
                att_weight = char_input.damage / denominator
                att_weights[char_input.character_id] = att_weight
                logging.warning(
                    f"[DEBUG] att_weight calc for char {char_input.character_id}: "
                    f"att_weight={att_weight}, damage={char_input.damage}, "
                    f"final_attack={base_char_stats.final_attack}, "
                    f"sup_multi={superiority_multiplier}, "
                    f"atk_multi={attack_multiplier}"
                )
            except (ZeroDivisionError, TypeError):
                att_weights[char_input.character_id] = 0

    # Step 2: Fetch all players in the union
    players_in_union = db.query(models.Player).filter(models.Player.union_id == request.union_id).all()

    # Step 3 & 4: Iterate through players and calculate simulated damage
    simulation_results = []
    for player in players_in_union:
        player_team_damages = {}
        for team in request.teams:
            team_total_damage = 0
            character_details = []

            # Get all character stats for the current player in one go
            player_character_ids = [char.character_id for char in team.characters]
            player_chars_stats = db.query(models.Character).filter(
                models.Character.player_id == player.id,
                models.Character.character_id.in_(player_character_ids)
            ).all()
            
            player_chars_map = {char.character_id: char for char in player_chars_stats}

            for char_input in team.characters:
                char_id = char_input.character_id
                att_weight = att_weights.get(char_id)

                # If we don't have a weight, we can't simulate
                if att_weight is None:
                    continue

                target_char_stats = player_chars_map.get(char_id)
                
                # If the player doesn't have this character, skip
                if not target_char_stats or not target_char_stats.final_attack:
                    simulated_damage = 0
                else:
                    element_weight = 1 if target_char_stats.element == team.element else 0
                    
                    # Forward calculation
                    attack_multiplier = (1 + (target_char_stats.total_stat_atk or 0) / 100)
                    superiority_multiplier_forward = (1 + element_weight * (target_char_stats.total_superiority or 0) / 100)
                    
                    logging.warning(
                        f"[DEBUG] Damage sim for player '{player.name}' char {char_id}: "
                        f"final_attack={target_char_stats.final_attack}, "
                        f"attack_multiplier={attack_multiplier}, "
                        f"sup_multi={superiority_multiplier_forward}, "
                        f"att_weight={att_weight}"
                    )

                    simulated_damage = (
                        target_char_stats.final_attack *
                        attack_multiplier *
                        superiority_multiplier_forward *
                        att_weight
                    )
                    # Ensure damage is not negative
                    simulated_damage = max(0, simulated_damage)

                team_total_damage += simulated_damage
                character_details.append(schemas.SimulatedCharacterDetail(
                    character_id=char_id,
                    name_cn=target_char_stats.name_cn if target_char_stats else "N/A",
                    simulated_damage=simulated_damage
                ))

            player_team_damages[team.element] = schemas.SimulatedTeamDamage(
                total_damage=team_total_damage,
                characters=character_details
            )

        simulation_results.append(schemas.SimulationPlayerResult(
            player_id=player.id,
            player_name=player.name,
            team_damages=player_team_damages
        ))

    return schemas.DamageSimulationResponse(simulation_results=simulation_results)