# Trigger reload
import json
import logging
import os
import uuid
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Query, Form, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import traceback
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from backend import models, schemas, auth, constants
from backend.database import get_async_db, AsyncSessionLocal
import sys
print("sys.path before logging_config import:", sys.path)
from backend.logging_config import setup_logging, request_id_var
from backend.services.user_service import UserService
from backend.services.auth_service import AuthService
from backend.services.union_service import UnionService

from backend.models import create_db_and_tables_async

# Set up logging
setup_logging()

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """
    Asynchronous startup event to create database tables.
    """
    await create_db_and_tables_async()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:15174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """
    Middleware to add a unique request_id to each incoming request.
    The request_id is stored in a context variable and added to the response headers.
    """
    # Generate a unique request ID
    request_id = str(uuid.uuid4())

    # Store it in the context variable
    request_id_var.set(request_id)

    logging.info(f"Request received: {request.method} {request.url.path}")

    # Process the request
    response = await call_next(request)

    # Add the request ID to the response headers
    response.headers["X-Request-ID"] = request_id

    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to catch all unhandled exceptions.
    Logs the exception with traceback and returns a generic 500 error response.
    """
    request_id = request_id_var.get()
    logging.error(
        f"Unhandled exception occurred for request_id: {request_id}",
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )


# --- Service Dependencies ---
async def get_user_service(db: AsyncSessionLocal = Depends(get_async_db)) -> UserService:
    return UserService(db)

async def get_auth_service(db: AsyncSessionLocal = Depends(get_async_db)) -> AuthService:
    return AuthService(db)

async def get_union_service(db: AsyncSessionLocal = Depends(get_async_db)) -> UnionService:
    return UnionService(db)

# --- API Endpoints ---

@app.get("/api/filter-options")
async def get_filter_options(user_service: UserService = Depends(get_user_service)):
    return await user_service.get_filter_options()

@app.post("/api/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, user_service: UserService = Depends(get_user_service)):
    db_user = await user_service.create_user(user)
    if not db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return db_user

@app.post("/api/auth/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.authenticate_user(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await auth_service.create_token_for_user(user=user)
    return {"access_token": access_token, "token_type": constants.TOKEN_TYPE}

@app.post("/api/upload/")
async def upload_file(
    files: List[UploadFile] = File(...),
    union_id: Optional[int] = Form(None),
    current_user: models.User = Depends(auth.get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    file_contents = {file.filename: await file.read() for file in files}
    try:
        successful_files, failed_files = await user_service.process_uploaded_files(
            file_contents, union_id, current_user.id
        )
        return {"successful_files": successful_files, "failed_files": failed_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during file processing: {e}")


@app.get("/api/characters/", response_model=List[schemas.CharacterResponse])
async def get_characters(
    player_name: Optional[str] = Query(None),
    union_ids: Optional[str] = Query(None),
    character_name: Optional[str] = Query(None),
    class_: Optional[str] = Query(None, alias="class"),
    element: Optional[str] = Query(None),
    weapon_type: Optional[str] = Query(None),
    use_burst_skill: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("absolute_training_degree"),
    order: Optional[str] = Query("desc"),
    user_service: UserService = Depends(get_user_service),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    try:
        return await user_service.get_characters_with_details(
            user_id=current_user.id, player_name=player_name, union_ids=union_ids,
            character_name=character_name, class_=class_, element=element,
            weapon_type=weapon_type, use_burst_skill=use_burst_skill,
            sort_by=sort_by, order=order
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/characters/all-unique", response_model=List[Dict[str, Any]])
async def get_all_unique_characters(user_service: UserService = Depends(get_user_service)):
    return await user_service.get_all_unique_characters()

@app.get("/api/settings/is-c", response_model=Dict[int, bool])
async def get_is_c_settings(user_service: UserService = Depends(get_user_service)):
    return await user_service.get_is_c_settings()

@app.post("/api/settings/is-c")
async def update_is_c_settings(settings: dict[int, bool], user_service: UserService = Depends(get_user_service), current_user: models.User = Depends(auth.get_current_admin_user)):
    await user_service.update_is_c_settings(settings)
    return {"status": "success"}

@app.get("/api/characters/{character_db_id}", response_model=Dict[str, Any])
async def get_character_details(character_db_id: int, user_service: UserService = Depends(get_user_service)):
    char_details = await user_service.get_character_details(character_db_id)
    if not char_details:
        raise HTTPException(status_code=404, detail="Character not found")
    return char_details

@app.delete("/api/players/{player_name}")
async def delete_player(
    player_name: str,
    user_service: UserService = Depends(get_user_service),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    success = await user_service.delete_player_and_data(player_name, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Player not found for the current user")
    return {"status": "success", "message": f"Player {player_name} and all associated data have been deleted."}

@app.delete("/api/clear-all-data")
async def clear_all_data(
    user_service: UserService = Depends(get_user_service),
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    try:
        await user_service.clear_all_user_data(current_user.id)
        return {"status": "success", "message": "All your data has been cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while clearing data: {e}")

@app.get("/api/players/", response_model=List[Dict[str, Any]])
async def get_players(
    union_ids: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("name"),
    order: Optional[str] = Query("asc"),
    user_service: UserService = Depends(get_user_service),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    try:
        return await user_service.get_players(current_user.id, union_ids, sort_by, order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/element-training-analysis/", response_model=List[Dict[str, Any]])
async def get_element_training_analysis(
    union_ids: Optional[str] = Form(None),
    character_coefficients: str = Form(...),
    training_type: str = Form("relative_training_degree"),
    user_service: UserService = Depends(get_user_service),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    try:
        return await user_service.get_element_training_analysis(
            user_id=current_user.id,
            union_ids=union_ids,
            character_coefficients=character_coefficients,
            training_type=training_type
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Union CRUD ---
@app.post("/api/unions/", response_model=schemas.Union)
async def create_union(
    union: schemas.UnionCreate,
    db: AsyncSessionLocal = Depends(get_async_db),
    union_service: UnionService = Depends(get_union_service),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_union = await union_service.create_union(db, union, current_user.id)
    return db_union

@app.get("/api/unions/", response_model=List[schemas.Union])
async def get_unions(
    union_service: UnionService = Depends(get_union_service),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    return await union_service.get_unions_by_user(current_user.id)

@app.put("/api/unions/{union_id}", response_model=schemas.Union)
async def update_union(
    union_id: int,
    union_update: schemas.UnionUpdate,
    union_service: UnionService = Depends(get_union_service),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    updated_union = await union_service.update_union(union_id, union_update.name, current_user.id)
    if not updated_union:
        raise HTTPException(status_code=404, detail="Union not found or you don't have permission to edit it")
    return updated_union

@app.delete("/api/unions/{union_id}", response_model=dict)
async def delete_union(
    union_id: int,
    union_service: UnionService = Depends(get_union_service),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    success = await union_service.delete_union(union_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Union not found or cannot be deleted (e.g., it has players).")
    return {"status": "success"}

# --- Damage Simulation ---
@app.post("/api/damage_simulation", response_model=schemas.DamageSimulationResponse)
async def post_damage_simulation(
    request: schemas.DamageSimulationRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Receives a damage simulation request and returns the calculated results.
    """
    try:
        simulation_results = await user_service.run_damage_simulation(request)
        return simulation_results
    except Exception as e:
        logging.error(f"Error during damage simulation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred during damage simulation.")

# --- Static Files ---
# Mount static files only in production. In development, frontend is served by Vite.
if os.getenv("APP_ENV") == constants.PROD_ENV:
    app.mount("/", StaticFiles(directory=constants.STATIC_DIR, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "18000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
