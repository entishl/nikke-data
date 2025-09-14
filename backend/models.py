from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./game_characters.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    synchro_level = Column(Integer)
    resilience_cube_level = Column(Integer, default=0)
    bastion_cube_level = Column(Integer, default=0)
    characters = relationship("Character", back_populates="player", cascade="all, delete-orphan")

class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    character_id = Column(Integer, index=True)
    name_cn = Column(String, index=True)
    element = Column(String)
    skill1_level = Column(Integer)
    skill2_level = Column(Integer)
    skill_burst_level = Column(Integer)
    limit_break_grade = Column(Integer)
    core = Column(Integer)
    item_level = Column(Integer)
    item_rare = Column(String)
    total_stat_atk = Column(Float, default=0.0)
    total_inc_element_dmg = Column(Float, default=0.0)
    total_stat_ammo_load = Column(Float, default=0.0)
    total_superiority = Column(Float, default=0.0)
    final_attack = Column(Float, default=0.0)
    absolute_training_degree = Column(Float, default=0.0)
    relative_training_degree = Column(Float, default=0.0)
    general_relative_training_degree = Column(Float, default=0.0)

    # New fields for filtering
    class_ = Column(String, index=True)
    corporation = Column(String, index=True)
    weapon_type = Column(String, index=True)
    original_rare = Column(String, index=True)
    use_burst_skill = Column(String, index=True)
    is_C = Column(Boolean, default=True, nullable=False)
    
    player = relationship("Player", back_populates="characters")
    equipments = relationship("Equipment", back_populates="character", cascade="all, delete-orphan")

class Equipment(Base):
    __tablename__ = "equipments"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    equipment_slot = Column(Integer)
    function_type = Column(String)
    function_value = Column(Float)
    level = Column(Integer)

    character = relationship("Character", back_populates="equipments")

class CharacterSetting(Base):
    __tablename__ = "character_settings"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, unique=True, index=True)
    is_C = Column(Boolean, default=True, nullable=False)

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)
