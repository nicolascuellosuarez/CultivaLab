from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from src.cultiva_lab.services import UserService, CropService, CropTypeService
from src.cultiva_lab.storage_supabase import SupabaseStorage
