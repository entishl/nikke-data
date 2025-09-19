# -*- coding: utf-8 -*-
"""
This module contains all the constant values used in the backend application.
By centralizing constants, we can avoid hardcoding values in the business logic,
making the application more maintainable and easier to configure.
"""

import os

# --- Authentication Constants ---
# Secret key for encoding and decoding JWTs.
# It is loaded from an environment variable for security.
SECRET_KEY = os.getenv("SECRET_KEY")

if SECRET_KEY is None:
    raise ValueError("SECRET_KEY environment variable not set. Application cannot start.")

# Algorithm used for JWT signing.
ALGORITHM = "HS256"

# Expiration time for access tokens, in minutes.
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- API Configuration ---
# Base path for all API routes.
# URL for the token endpoint.
TOKEN_URL = "/api/auth/token"
API_V1_STR = "/api/v1"

# --- Database Constants ---
# Default database URL.
# For production, this should be configured via environment variables.
DATABASE_URL = "sqlite:///./lucky.db"

# --- User Roles ---
# Default role for new users.
DEFAULT_USER_ROLE = "user"
# Token type for authentication.
TOKEN_TYPE = "bearer"

# --- Environment Settings ---
# Environment name for production.
PROD_ENV = "production"

# Directory for static files in production.
STATIC_DIR = "/app/static"
# --- Game Logic Constants ---
# Coefficients for calculating breakthrough value
LIMIT_BREAK_GRADE_COEFFICIENT = 0.03
CORE_ENHANCEMENT_COEFFICIENT = 0.02

# List of elements
ELEMENTS = ["Fire", "Water", "Wind", "Electronic", "Iron"]

# Special character ID mappings (e.g., Rapi: Red Hood)
SPECIAL_CHARACTER_ID_MAP = {
    201601: 201602  # Rapi: Red Hood -> Virtual Red Hood
}
VIRTUAL_RED_HOOD_ID = 201602
RED_HOOD_ID = 201601

# Cube names
RESILIENCE_CUBE_NAME = "遗迹巨熊魔方"
BASTION_CUBE_NAME = "战术巨熊魔方"

# Base value for superiority calculation
BASE_SUPERIORITY = 10

# Element names used in logic
UTILITY_ELEMENT = "Utility"
VIRTUAL_RH_ELEMENT = "Iron"
# --- Sorting Constants ---
# Default sort order
DESC_ORDER = "desc"