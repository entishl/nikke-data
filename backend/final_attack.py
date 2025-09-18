# backend/final_attack.py

def translate_class_name(class_en: str) -> str:
    """
    将英文职业名称转换为中文。
    """
    translation_map = {
        "Attacker": "火力型",
        "Supporter": "辅助型",
        "Defender": "防御型",
    }
    return translation_map.get(class_en, "")

def calculate_base_breakthrough_attack(sync_attack: float, grade: int) -> float:
    """
    计算基础突破攻击力。
    """
    return sync_attack * (1 + 0.02 * grade) + (20 * grade)

def calculate_favor_rank(grade: int, corporation: str, character_id: int, super_character_ids: list) -> int:
    """
    计算好感度等级。
    """
    rank = (grade + 1) * 10
    is_pilgrim = (corporation == 'PILGRIM')
    is_super = (character_id in super_character_ids)
    if not is_pilgrim and not is_super:
        return min(rank, 30)
    return rank

def get_favor_attack_bonus(rank: int, character_class_en: str, rank_data: dict) -> float:
    """
    根据好感度等级和职业查找攻击力加成。
    """
    class_cn = translate_class_name(character_class_en)
    if not class_cn:
        return 0.0
    try:
        return float(rank_data.get(str(rank), {}).get(class_cn, {}).get('attack', 0))
    except (KeyError, TypeError, ValueError):
        return 0.0

def calculate_coor_bonus(coor_level: int) -> int:
    """
    计算协同等级加成。
    """
    return coor_level * 25

def apply_core_multiplier(current_attack_sum: float, core: int) -> float:
    """
    应用核心乘数。
    """
    return current_attack_sum * (1 + 0.02 * core)

def get_equipment_attack(character_class_en: str, equipment_data: dict) -> int:
    """
    获取装备攻击力。
    """
    key_map = {
        "Attacker": "attackers",
        "Defender": "defenders",
        "Supporter": "supports",
    }
    lookup_key = key_map.get(character_class_en)
    if not lookup_key:
        return 0
    return int(equipment_data.get(lookup_key, 0))

def get_item_attack(item_rare: str, item_level: int, number_data: dict) -> int:
    """
    根据物品稀有度和等级查找攻击力。
    """
    if item_rare == "SSR":
        return 9688
    elif item_rare == "SR":
        item_atk_list = number_data.get("item_atk", [])
        item_level_idx = item_level - 1
        if 0 <= item_level_idx < len(item_atk_list):
            return item_atk_list[item_level_idx]
    return 0

def get_cube_attack(cube_level: int, cube_data: list) -> int:
    """
    根据魔方等级查找攻击力。
    """
    for item in cube_data:
        if item.get("cube_level") == cube_level:
            return item.get("atk", 0)
    return 0

def _prepare_attack_components(
    sync_attack: float,
    grade: int,
    corporation: str,
    character_id: int,
    super_character_ids: list,
    character_class_en: str,
    rank_data: dict,
    coor_level: int,
    equipment_data: dict,
    item_rare: str,
    item_level: int,
    number_data: dict,
    core: int,
    cube_level: int,
    cube_data: list
) -> dict:
    """
    阶段一：准备所有攻击力组件。
    """
    base_breakthrough_attack = calculate_base_breakthrough_attack(sync_attack, grade)
    
    favor_rank = calculate_favor_rank(grade, corporation, character_id, super_character_ids)
    favor_attack_bonus = get_favor_attack_bonus(favor_rank, character_class_en, rank_data)
    
    coor_bonus = calculate_coor_bonus(coor_level)
    
    equipment_attack = get_equipment_attack(character_class_en, equipment_data)
    
    item_attack = get_item_attack(item_rare, item_level, number_data)
    
    cube_attack = get_cube_attack(cube_level, cube_data)
    
    return {
        "base_breakthrough_attack": base_breakthrough_attack,
        "favor_attack_bonus": favor_attack_bonus,
        "coor_bonus": coor_bonus,
        "equipment_attack": equipment_attack,
        "item_attack": item_attack,
        "core": core,
        "cube_attack": cube_attack
    }

def _execute_final_calculation(components: dict) -> float:
    """
    阶段二：执行最终计算。
    """
    base_sum = (
        components["base_breakthrough_attack"] +
        components["favor_attack_bonus"] +
        components["coor_bonus"]
    )
    
    multiplied_sum = apply_core_multiplier(base_sum, components["core"])
    
    final_attack = (
        multiplied_sum +
        components["equipment_attack"] +
        components["item_attack"] +
        components["cube_attack"]
    )
    
    return final_attack

def calculate_final_attack(
    sync_attack: float,
    grade: int,
    corporation: str,
    character_id: int,
    super_character_ids: list,
    character_class_en: str,
    rank_data: dict,
    coor_level: int,
    equipment_data: dict,
    item_rare: str,
    item_level: int,
    number_data: dict,
    core: int,
    cube_level: int,
    cube_data: list
) -> float:
    """
    主函数：计算最终攻击力。
    """
    components = _prepare_attack_components(
        sync_attack, grade, corporation, character_id, super_character_ids,
        character_class_en, rank_data, coor_level, equipment_data,
        item_rare, item_level, number_data, core, cube_level, cube_data
    )
    
    final_attack = _execute_final_calculation(components)
    
    return final_attack