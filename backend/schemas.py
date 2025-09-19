from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class PlayerBase(BaseModel):
    name: str
    synchro_level: int
    resilience_cube_level: int
    bastion_cube_level: int
    union_id: Optional[int] = None

class PlayerCreate(PlayerBase):
    user_id: int

class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    synchro_level: Optional[int] = None
    resilience_cube_level: Optional[int] = None
    bastion_cube_level: Optional[int] = None
    union_id: Optional[int] = None

class CharacterResponse(BaseModel):
    id: int
    player_name: Optional[str] = None
    union_id: Optional[int] = None
    union_name: Optional[str] = None
    character_id: Optional[int] = None
    name_cn: Optional[str] = None
    element: Optional[str] = None
    element_from_user: Optional[str] = None
    skill1_level: Optional[int] = None
    skill2_level: Optional[int] = None
    skill_burst_level: Optional[int] = None
    limit_break_grade: Optional[int] = None
    core: Optional[int] = None
    item_level: Optional[int] = None
    item_rare: Optional[str] = None
    total_stat_atk: Optional[float] = None
    total_inc_element_dmg: Optional[float] = None
    total_stat_ammo_load: Optional[float] = None
    total_superiority: Optional[float] = None
    absolute_training_degree: Optional[float] = None
    relative_training_degree: Optional[float] = None
    general_relative_training_degree: Optional[float] = None
    class_: Optional[str] = None
    corporation: Optional[str] = None
    weapon_type: Optional[str] = None
    original_rare: Optional[str] = None
    use_burst_skill: Optional[str] = None
    is_C: Optional[bool] = None
    breakthrough_coefficient: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


# --- Damage Simulation Models ---

# Request Models
class SimulationCharacter(BaseModel):
    character_id: int
    damage: float

class SimulationTeam(BaseModel):
    element: str
    characters: List[SimulationCharacter]

class DamageSimulationRequest(BaseModel):
    union_id: int
    base_player_id: int
    teams: List[SimulationTeam]
    coor_level: Optional[int] = 0

# Response Models
class SimulatedCharacterDetail(BaseModel):
    character_id: int
    name_cn: str
    simulated_damage: float

class SimulatedTeamDamage(BaseModel):
    total_damage: float
    characters: List[SimulatedCharacterDetail]

class SimulationPlayerResult(BaseModel):
    player_id: int
    player_name: str
    team_damages: Dict[str, SimulatedTeamDamage]

class DamageSimulationResponse(BaseModel):
    simulation_results: List[SimulationPlayerResult]

class UnionCreate(BaseModel):
    name: str

class UnionUpdate(BaseModel):
    name: Optional[str] = None

class Union(BaseModel):
    id: int
    name: str
    user_id: int

    class Config:
        from_attributes = True