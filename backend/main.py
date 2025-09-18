# Trigger reload
import json
import os
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Query, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from backend import models, services, schemas
from backend.models import SessionLocal, engine
from backend.utils import NIKKE_LIST_DATA

models.create_db_and_tables()

app = FastAPI()



# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/filter-options")
def get_filter_options():
    nikkes = NIKKE_LIST_DATA.get('nikkes', [])
    
    # Use sets to get unique values
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

@app.post("/api/upload/")
async def upload_file(files: List[UploadFile] = File(...), union_id: Optional[int] = Form(None), db: Session = Depends(get_db)):
    successful_files = 0
    failed_files = 0

    # Step 1: Pre-process to gather all character IDs from all files
    all_character_ids = set()
    file_contents = {}
    for file in files:
        contents = await file.read()
        try:
            data = json.loads(contents)
            file_contents[file.filename] = data
            for element, characters_in_element in data.get("elements", {}).items():
                for char_data in characters_in_element:
                    if "id" in char_data:
                        all_character_ids.add(char_data["id"])
                        if char_data["id"] == 201601: # Rapi: Red Hood
                            all_character_ids.add(201602)
        except json.JSONDecodeError:
            failed_files += 1
            print(f"Failed to decode JSON from file {file.filename}")
            continue

    # Step 2: Batch query for CharacterSettings
    is_c_settings = {}
    if all_character_ids:
        settings = db.query(models.CharacterSetting).filter(models.CharacterSetting.character_id.in_(all_character_ids)).all()
        is_c_settings = {setting.character_id: setting.is_C for setting in settings}

    # Step 3: Process each file using the service layer
    for file in files:
        data = file_contents.get(file.filename)
        if not data:
            continue # Already handled in pre-processing

        try:
            services.process_upload_data(db, data, union_id, is_c_settings)
            successful_files += 1
        except Exception as e:
            db.rollback()
            failed_files += 1
            print(f"Failed to process file {file.filename}: {e}")

    return {"successful_files": successful_files, "failed_files": failed_files}

@app.get("/api/characters/", response_model=List[schemas.CharacterResponse])
def get_characters(
    player_name: Optional[str] = Query(None),
    union_ids: Optional[str] = Query(None),
    character_name: Optional[str] = Query(None),
    class_: Optional[str] = Query(None, alias="class"),
    element: Optional[str] = Query(None),
    weapon_type: Optional[str] = Query(None),
    use_burst_skill: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("absolute_training_degree"),
    order: Optional[str] = Query("desc"),
    db: Session = Depends(get_db)
):
    try:
        characters = services.get_characters_service(
            db, player_name, union_ids, character_name, class_, element,
            weapon_type, use_burst_skill, sort_by, order
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    result = []
    for char in characters:
        grade = char.limit_break_grade or 0
        core = char.core or 0
        breakthrough_coefficient = 1 + (grade * 0.03) + (core * 0.02)
        
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

@app.get("/api/characters/all-unique")
def get_all_unique_characters(db: Session = Depends(get_db)):
    # Query for distinct character_id, name_cn, and element from the Character table
    query = db.query(models.Character.character_id, models.Character.name_cn, models.Character.element, models.Character.element_from_user).distinct()
    
    # Execute the query and format the results
    unique_characters = [
        {"id": char_id, "name_cn": name_cn, "element": element, "element_from_user": element_from_user}
        for char_id, name_cn, element, element_from_user in query.all()
    ]
    
    # Sort the results by character ID
    return sorted(unique_characters, key=lambda x: x['id'])

@app.get("/api/settings/is-c")
def get_is_c_settings(db: Session = Depends(get_db)):
    settings = db.query(models.CharacterSetting).all()
    return {setting.character_id: setting.is_C for setting in settings}

@app.post("/api/settings/is-c")
def update_is_c_settings(settings: dict[int, bool], db: Session = Depends(get_db)):
    for char_id, is_c in settings.items():
        # First, update the setting in the CharacterSetting table for future uploads
        setting = db.query(models.CharacterSetting).filter_by(character_id=char_id).first()
        if setting:
            setting.is_C = is_c
        else:
            setting = models.CharacterSetting(character_id=char_id, is_C=is_c)
            db.add(setting)
        
        # Second, update the is_C status for all existing characters in the Character table
        db.query(models.Character).filter(
            models.Character.character_id == char_id
        ).update({"is_C": is_c})

    db.commit()
    return {"status": "success"}

@app.get("/api/characters/{character_db_id}")
def get_character_details(character_db_id: int, db: Session = Depends(get_db)):
    char = db.query(models.Character).filter(models.Character.id == character_db_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")

    equipments = []
    for equip in char.equipments:
        equipments.append({
            "equipment_slot": equip.equipment_slot,
            "function_type": equip.function_type,
            "function_value": equip.function_value,
            "level": equip.level,
        })

    grade = char.limit_break_grade or 0
    core = char.core or 0
    breakthrough_coefficient = 1 + (grade * 0.03) + (core * 0.02)

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

@app.delete("/api/players/{player_name}")
def delete_player(player_name: str, db: Session = Depends(get_db)):
    # Find the player by name
    player = db.query(models.Player).filter(models.Player.name == player_name).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Delete all characters associated with the player
    # The cascade delete on equipments will handle those
    db.query(models.Character).filter(models.Character.player_id == player.id).delete()

    # Now delete the player
    db.delete(player)
    
    db.commit()
    return {"status": "success", "message": f"Player {player_name} and all associated data have been deleted."}

@app.delete("/api/clear-all-data")
def clear_all_data(db: Session = Depends(get_db)):
    try:
        # The order of deletion matters due to foreign key constraints.
        # Start with Equipment, then Character, then Player.
        db.query(models.Equipment).delete()
        db.query(models.Character).delete()
        db.query(models.Player).delete()
        db.query(models.Union).delete()
        db.query(models.CharacterSetting).delete()
        db.commit()
        return {"status": "success", "message": "All data has been cleared."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred while clearing data: {e}")


@app.get("/api/players/", response_model=List[dict])
def get_players(
    union_ids: Optional[str] = Query(None), # Changed from union_id to union_ids
    sort_by: Optional[str] = Query("name"),
    order: Optional[str] = Query("asc"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Player)
    if union_ids:
        try:
            union_id_list = [int(uid.strip()) for uid in union_ids.split(',') if uid.strip()]
            if union_id_list:
                query = query.filter(models.Player.union_id.in_(union_id_list))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid union_ids format. Must be comma-separated integers.")

    sort_column = getattr(models.Player, sort_by, None)
    if sort_column is None:
        raise HTTPException(status_code=400, detail=f"Invalid sort key: {sort_by}")

    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
        
    players = query.all()
    
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

@app.post("/api/element-training-analysis/")
def get_element_training_analysis(
    union_ids: Optional[str] = Form(None),
    character_coefficients: str = Form(...),
    training_type: str = Form("relative_training_degree"),
    db: Session = Depends(get_db)
):
    try:
        coeffs = json.loads(character_coefficients)
        character_ids = [int(k) for k in coeffs.keys()]
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid character_coefficients format.")

    if not character_ids:
        return []

    # 1. Get players
    player_query = db.query(models.Player)
    if union_ids:
        try:
            union_id_list = [int(uid.strip()) for uid in union_ids.split(',') if uid.strip()]
            if union_id_list:
                player_query = player_query.filter(models.Player.union_id.in_(union_id_list))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid union_ids format.")
    
    players = player_query.all()
    if not players:
        return []

    player_ids = [p.id for p in players]

    # 2. Get relevant characters for these players
    characters = db.query(models.Character).filter(
        models.Character.player_id.in_(player_ids),
        models.Character.character_id.in_(character_ids)
    ).all()

    # 3. Initialize results map
    analysis_results = {
        p.name: {"player_name": p.name, "elements": {"Fire": 0, "Water": 0, "Wind": 0, "Electronic": 0, "Iron": 0}}
        for p in players
    }

    # 4. Process characters
    for char in characters:
        coefficient = coeffs.get(str(char.character_id))
        if coefficient is not None:
            training_value = getattr(char, training_type, 0)
            player_name = char.player.name
            if player_name in analysis_results:
                analysis_results[player_name]["elements"][char.element] += training_value * float(coefficient)

    return list(analysis_results.values())

# Union CRUD
@app.post("/api/unions/", response_model=dict)
async def create_union(union: schemas.UnionCreate, db: Session = Depends(get_db)):
    db_union = models.Union(name=union.name)
    db.add(db_union)
    db.commit()
    db.refresh(db_union)
    return {"id": db_union.id, "name": db_union.name}

@app.get("/api/unions/", response_model=List[dict])
def get_unions(db: Session = Depends(get_db)):
    unions = db.query(models.Union).all()
    return [{"id": u.id, "name": u.name} for u in unions]

@app.put("/api/unions/{union_id}", response_model=dict)
def update_union(union_id: int, name: str, db: Session = Depends(get_db)):
    db_union = db.query(models.Union).filter(models.Union.id == union_id).first()
    if not db_union:
        raise HTTPException(status_code=404, detail="Union not found")
    db_union.name = name
    db.commit()
    db.refresh(db_union)
    return {"id": db_union.id, "name": db_union.name}

@app.delete("/api/unions/{union_id}", response_model=dict)
def delete_union(union_id: int, db: Session = Depends(get_db)):
    db_union = db.query(models.Union).filter(models.Union.id == union_id).first()
    if not db_union:
        raise HTTPException(status_code=404, detail="Union not found")
    
    # Optional: Check if any players are in this union before deleting
    if db_union.players:
        raise HTTPException(status_code=400, detail="Cannot delete union with players in it")

    db.delete(db_union)
    db.commit()
    return {"status": "success"}

@app.get("/api/unions/{union_id}/players", response_model=List[dict])
def get_union_players_temp_for_logging(union_id: int, db: Session = Depends(get_db)):
    print(f"DIAGNOSIS: Frontend called the incorrect endpoint /api/unions/{union_id}/players.")
    # This is a temporary endpoint for diagnosis.
    # The correct endpoint is /api/players/?union_ids={union_id}
    # Returning an empty list to prevent frontend errors during diagnosis.
    
    # For now, let's try to return the correct data to see if it fixes the UI
    players = db.query(models.Player).filter(models.Player.union_id == union_id).all()
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

@app.post("/api/damage_simulation", response_model=schemas.DamageSimulationResponse)
def post_damage_simulation(
    request: schemas.DamageSimulationRequest,
    db: Session = Depends(get_db)
):
    """
    Receives a damage simulation request and returns the calculated results.
    """
    try:
        simulation_results = services.run_damage_simulation(db, request)
        return simulation_results
    except Exception as e:
        # It's good practice to log the exception here
        print(f"Error during damage simulation: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred during damage simulation.")

# Mount static files only in production. In development, frontend is served by Vite.
if os.getenv("APP_ENV") == "production":
    app.mount("/", StaticFiles(directory="/app/static", html=True), name="static")

