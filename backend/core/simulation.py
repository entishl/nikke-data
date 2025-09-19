from typing import List, Dict, Optional
from pydantic import BaseModel
from backend import schemas

# Define data structures for pure functions to avoid dependency on ORM models
class CharacterStats(BaseModel):
    """A simplified character model for simulation calculations."""
    character_id: int
    name_cn: str
    element: str
    final_attack: Optional[float] = 0
    total_superiority: Optional[float] = 0
    total_stat_atk: Optional[float] = 0

class PlayerForSim(BaseModel):
    """A simplified player model for simulation, containing their relevant characters."""
    id: int
    name: str
    characters: List[CharacterStats]

def calculate_attribute_weights(
    teams: List[schemas.SimulationTeam],
    base_chars_map: Dict[int, CharacterStats],
) -> Dict[int, float]:
    """
    Calculates attribute weights based on a base player's damage output.
    This is a pure function, free of I/O operations.
    """
    att_weights = {}
    for team in teams:
        for char_input in team.characters:
            char_id = char_input.character_id
            base_char_stats = base_chars_map.get(char_id)

            if not base_char_stats or not base_char_stats.final_attack:
                att_weights[char_id] = 0
                continue
            
            element_weight = 1 if base_char_stats.element == team.element else 0
            superiority_multiplier = 1 + (element_weight * (base_char_stats.total_superiority or 0) / 100)
            attack_multiplier = 1 + ((base_char_stats.total_stat_atk or 0) / 100)
            denominator = base_char_stats.final_attack * superiority_multiplier * attack_multiplier
            att_weights[char_id] = char_input.damage / denominator if denominator != 0 else 0
    return att_weights

def run_player_simulations(
    players_in_union: List[PlayerForSim],
    teams: List[schemas.SimulationTeam],
    att_weights: Dict[int, float],
) -> List[schemas.SimulationPlayerResult]:
    """
    Runs the damage simulation for all players in a union using pre-calculated weights.
    This is a pure function, free of I/O operations.
    """
    simulation_results = []
    for player in players_in_union:
        player_team_damages = {}
        # Create a map of the preloaded characters for the current player for quick access
        player_chars_map = {char.character_id: char for char in player.characters}

        for team in teams:
            team_total_damage = 0
            character_details = []
            team_is_valid = True

            for char_input in team.characters:
                char_id = char_input.character_id
                att_weight = att_weights.get(char_id, 0)

                target_char_stats = player_chars_map.get(char_id)
                if not target_char_stats:
                    team_is_valid = False
                    break
                
                simulated_damage = 0
                if target_char_stats.final_attack:
                    element_weight = 1 if target_char_stats.element == team.element else 0
                    attack_multiplier = (1 + (target_char_stats.total_stat_atk or 0) / 100)
                    superiority_multiplier_forward = (1 + element_weight * (target_char_stats.total_superiority or 0) / 100)
                    simulated_damage = max(0, target_char_stats.final_attack * attack_multiplier * superiority_multiplier_forward * att_weight)
                
                team_total_damage += simulated_damage
                character_details.append(schemas.SimulatedCharacterDetail(
                    character_id=char_id, name_cn=target_char_stats.name_cn, simulated_damage=simulated_damage
                ))
            
            player_team_damages[team.element] = schemas.SimulatedTeamDamage(
                total_damage=team_total_damage if team_is_valid else 0.0,
                characters=character_details if team_is_valid else []
            )
        simulation_results.append(schemas.SimulationPlayerResult(
            player_id=player.id, player_name=player.name, team_damages=player_team_damages
        ))
        
    return simulation_results