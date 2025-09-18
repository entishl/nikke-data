import json
from pathlib import Path

def load_static_data():
    """Loads all static JSON data files."""
    current_dir = Path(__file__).parent
    
    # Load nikke list for static data
    with open(current_dir / 'list.json', 'r', encoding='utf-8') as f:
        nikke_list_data = json.load(f)
    nikke_static_data = {nikke['id']: nikke for nikke in nikke_list_data['nikkes']}
    
    # Load cube data
    with open(current_dir / 'cube.json', 'r', encoding='utf-8') as f:
        cube_data = json.load(f)
    cube_level_map = {item['cube_level']: item for item in cube_data}
    
    # Load number data
    with open(current_dir / 'number.json', 'r', encoding='utf-8') as f:
        number_data = json.load(f)

    # Load rank data
    with open(current_dir / 'rank.json', 'r', encoding='utf-8') as f:
        rank_data = json.load(f)

    # Load equipment data
    with open(current_dir / 'equipment.json', 'r', encoding='utf-8') as f:
        equipment_data = json.load(f)

    # Load super data
    with open(current_dir / 'super.json', 'r', encoding='utf-8') as f:
        super_data = json.load(f)
        
    return nikke_list_data, nikke_static_data, cube_level_map, number_data, rank_data, equipment_data, super_data

# Load data on module import
NIKKE_LIST_DATA, NIKKE_STATIC_DATA, CUBE_LEVEL_MAP, NUMBER_DATA, RANK_DATA, EQUIPMENT_DATA, SUPER_DATA = load_static_data()